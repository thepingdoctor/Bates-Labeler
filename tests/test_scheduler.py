"""Tests for batch scheduler module."""

import pytest
import time
from datetime import datetime, timedelta
from pathlib import Path
from bates_labeler.scheduler import (
    BatchScheduler,
    Job,
    JobStatus,
    JobType,
    SCHEDULER_AVAILABLE
)


pytestmark = pytest.mark.skipif(
    not SCHEDULER_AVAILABLE,
    reason="APScheduler not installed"
)


@pytest.fixture
def scheduler():
    """Create BatchScheduler instance."""
    if SCHEDULER_AVAILABLE:
        sched = BatchScheduler(max_concurrent_jobs=2)
        sched.start()
        yield sched
        sched.shutdown(wait=False)


@pytest.fixture
def sample_config():
    """Sample job configuration."""
    return {
        'input_files': ['file1.pdf', 'file2.pdf'],
        'output_dir': '/tmp/output',
        'prefix': 'TEST-'
    }


def sample_process_func(config):
    """Sample processing function for testing."""
    time.sleep(0.1)  # Simulate work
    return {'processed': len(config.get('input_files', [])), 'status': 'success'}


def failing_process_func(config):
    """Failing processing function for testing."""
    raise ValueError("Intentional test failure")


class TestJob:
    """Test Job class."""

    def test_initialization(self):
        """Test job initialization."""
        config = {'test': 'value'}
        job = Job(
            job_id="job_1",
            name="Test Job",
            job_type=JobType.ONE_TIME,
            config=config
        )

        assert job.job_id == "job_1"
        assert job.name == "Test Job"
        assert job.job_type == JobType.ONE_TIME
        assert job.status == JobStatus.PENDING
        assert job.config == config

    def test_to_dict(self):
        """Test job serialization."""
        job = Job(
            job_id="job_1",
            name="Test Job",
            job_type=JobType.RECURRING,
            config={'test': 'value'}
        )

        data = job.to_dict()
        assert data['job_id'] == "job_1"
        assert data['name'] == "Test Job"
        assert data['job_type'] == JobType.RECURRING.value
        assert data['status'] == JobStatus.PENDING.value


class TestBatchScheduler:
    """Test BatchScheduler class."""

    def test_initialization(self):
        """Test scheduler initialization."""
        if not SCHEDULER_AVAILABLE:
            pytest.skip("APScheduler not available")

        scheduler = BatchScheduler(max_concurrent_jobs=3)
        assert scheduler.max_concurrent_jobs == 3
        assert not scheduler.scheduler.running

        scheduler.shutdown()

    def test_start_shutdown(self, scheduler):
        """Test scheduler start and shutdown."""
        assert scheduler.scheduler.running

        scheduler.shutdown(wait=False)
        assert not scheduler.scheduler.running

    def test_schedule_one_time_job(self, scheduler, sample_config):
        """Test scheduling one-time job."""
        run_date = datetime.now() + timedelta(seconds=1)

        job_id = scheduler.schedule_one_time_job(
            name="One Time Test",
            run_date=run_date,
            process_func=sample_process_func,
            config=sample_config
        )

        assert job_id is not None
        assert job_id in scheduler.jobs

        job = scheduler.jobs[job_id]
        assert job.name == "One Time Test"
        assert job.job_type == JobType.ONE_TIME
        assert job.status == JobStatus.PENDING

    def test_schedule_recurring_job(self, scheduler, sample_config):
        """Test scheduling recurring job."""
        # Every minute
        cron_expression = "* * * * *"

        job_id = scheduler.schedule_recurring_job(
            name="Recurring Test",
            cron_expression=cron_expression,
            process_func=sample_process_func,
            config=sample_config
        )

        assert job_id is not None
        assert job_id in scheduler.jobs

        job = scheduler.jobs[job_id]
        assert job.name == "Recurring Test"
        assert job.job_type == JobType.RECURRING

    def test_schedule_interval_job(self, scheduler, sample_config):
        """Test scheduling interval job."""
        job_id = scheduler.schedule_interval_job(
            name="Interval Test",
            interval_seconds=5,
            process_func=sample_process_func,
            config=sample_config
        )

        assert job_id is not None
        assert job_id in scheduler.jobs

    def test_setup_watch_folder(self, scheduler, sample_config, tmp_path):
        """Test watch folder setup."""
        watch_dir = tmp_path / "watch"

        job_id = scheduler.setup_watch_folder(
            name="Watch Test",
            watch_path=watch_dir,
            process_func=sample_process_func,
            config=sample_config,
            pattern="*.pdf",
            interval_seconds=2
        )

        assert job_id is not None
        assert watch_dir.exists()

        job = scheduler.jobs[job_id]
        assert job.job_type == JobType.WATCH_FOLDER
        assert 'watch_path' in job.config

    def test_job_execution(self, scheduler, sample_config):
        """Test job execution."""
        # Schedule immediate job
        run_date = datetime.now() + timedelta(seconds=0.5)

        job_id = scheduler.schedule_one_time_job(
            name="Execution Test",
            run_date=run_date,
            process_func=sample_process_func,
            config=sample_config
        )

        # Wait for job to execute
        time.sleep(1)

        job = scheduler.jobs[job_id]
        assert job.status == JobStatus.COMPLETED
        assert job.result is not None
        assert job.result['status'] == 'success'

    def test_job_failure_handling(self, scheduler, sample_config):
        """Test job failure handling."""
        run_date = datetime.now() + timedelta(seconds=0.5)

        job_id = scheduler.schedule_one_time_job(
            name="Failure Test",
            run_date=run_date,
            process_func=failing_process_func,
            config=sample_config
        )

        # Wait for job to fail
        time.sleep(1)

        job = scheduler.jobs[job_id]
        assert job.status == JobStatus.FAILED
        assert job.error is not None
        assert "Intentional test failure" in job.error

    def test_cancel_job(self, scheduler, sample_config):
        """Test job cancellation."""
        # Schedule future job
        run_date = datetime.now() + timedelta(seconds=10)

        job_id = scheduler.schedule_one_time_job(
            name="Cancel Test",
            run_date=run_date,
            process_func=sample_process_func,
            config=sample_config
        )

        # Cancel immediately
        cancelled = scheduler.cancel_job(job_id)
        assert cancelled is True

        job = scheduler.jobs[job_id]
        assert job.status == JobStatus.CANCELLED

    def test_get_job_status(self, scheduler, sample_config):
        """Test job status retrieval."""
        run_date = datetime.now() + timedelta(seconds=10)

        job_id = scheduler.schedule_one_time_job(
            name="Status Test",
            run_date=run_date,
            process_func=sample_process_func,
            config=sample_config
        )

        status = scheduler.get_job_status(job_id)
        assert status is not None
        assert status['job_id'] == job_id
        assert status['name'] == "Status Test"
        assert status['status'] == JobStatus.PENDING.value

        # Non-existent job
        assert scheduler.get_job_status("nonexistent") is None

    def test_list_jobs(self, scheduler, sample_config):
        """Test job listing."""
        # Create jobs with different statuses
        job1_id = scheduler.schedule_one_time_job(
            name="Job 1",
            run_date=datetime.now() + timedelta(seconds=10),
            process_func=sample_process_func,
            config=sample_config
        )

        job2_id = scheduler.schedule_recurring_job(
            name="Job 2",
            cron_expression="* * * * *",
            process_func=sample_process_func,
            config=sample_config
        )

        # List all jobs
        all_jobs = scheduler.list_jobs()
        assert len(all_jobs) >= 2

        # Filter by type
        one_time_jobs = scheduler.list_jobs(job_type=JobType.ONE_TIME)
        assert len(one_time_jobs) >= 1

        recurring_jobs = scheduler.list_jobs(job_type=JobType.RECURRING)
        assert len(recurring_jobs) >= 1

    def test_get_running_jobs(self, scheduler, sample_config):
        """Test getting running jobs."""
        # Initially no running jobs
        running = scheduler.get_running_jobs()
        assert len(running) == 0

        # Note: Testing running jobs is difficult due to timing
        # In real usage, jobs would show as running during execution

    def test_max_concurrent_jobs(self, scheduler, sample_config):
        """Test concurrent job limit."""
        # Scheduler configured with max_concurrent_jobs=2

        def slow_process(config):
            time.sleep(2)
            return {'status': 'success'}

        # Schedule multiple jobs to run simultaneously
        for i in range(3):
            scheduler.schedule_one_time_job(
                name=f"Concurrent {i}",
                run_date=datetime.now() + timedelta(seconds=0.1),
                process_func=slow_process,
                config=sample_config
            )

        # Wait briefly
        time.sleep(0.5)

        # Should have at most 2 running jobs
        running = scheduler.get_running_jobs()
        assert len(running) <= 2

    def test_invalid_cron_expression(self, scheduler, sample_config):
        """Test invalid cron expression handling."""
        with pytest.raises(ValueError):
            scheduler.schedule_recurring_job(
                name="Invalid Cron",
                cron_expression="invalid",
                process_func=sample_process_func,
                config=sample_config
            )

    def test_watch_folder_processing(self, scheduler, sample_config, tmp_path):
        """Test watch folder file processing."""
        watch_dir = tmp_path / "watch"
        watch_dir.mkdir()

        processed_files = []

        def watch_process_func(file_path, config):
            processed_files.append(file_path)
            return {'status': 'success'}

        job_id = scheduler.setup_watch_folder(
            name="Watch Process Test",
            watch_path=watch_dir,
            process_func=watch_process_func,
            config=sample_config,
            pattern="*.pdf",
            interval_seconds=1
        )

        # Create test files
        (watch_dir / "file1.pdf").touch()
        (watch_dir / "file2.pdf").touch()

        # Wait for processing
        time.sleep(2)

        # Files should be processed
        assert len(processed_files) >= 1

    def test_job_id_generation(self, scheduler):
        """Test unique job ID generation."""
        config = {}
        job_ids = set()

        for i in range(10):
            job_id = scheduler._generate_job_id()
            assert job_id not in job_ids
            job_ids.add(job_id)

        assert len(job_ids) == 10
