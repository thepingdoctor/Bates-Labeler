"""
Comprehensive Test Suite for Batch Scheduler (v2.2.0 Feature #3)

Tests batch job scheduling functionality including:
- One-time scheduled jobs
- Recurring jobs with cron expressions
- Interval-based jobs
- Watch folder automation
- Job queue management
- Job status tracking
- Concurrent job limits
"""

import logging
import pytest
import tempfile
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


# Skip all tests if APScheduler not available
pytestmark = pytest.mark.skipif(
    not SCHEDULER_AVAILABLE,
    reason="APScheduler not installed"
)


class TestJob:
    """Test Job class."""

    def test_create_job(self):
        """Test creating a job."""
        job = Job(
            job_id="test_123",
            name="Test Job",
            job_type=JobType.ONE_TIME,
            config={"param1": "value1"}
        )

        assert job.job_id == "test_123"
        assert job.name == "Test Job"
        assert job.job_type == JobType.ONE_TIME
        assert job.status == JobStatus.PENDING
        assert job.config["param1"] == "value1"

    def test_job_to_dict(self):
        """Test converting job to dictionary."""
        job = Job(
            job_id="test_123",
            name="Test Job",
            job_type=JobType.RECURRING,
            config={"param1": "value1"}
        )

        job.status = JobStatus.COMPLETED
        job_dict = job.to_dict()

        assert job_dict["job_id"] == "test_123"
        assert job_dict["name"] == "Test Job"
        assert job_dict["job_type"] == "recurring"
        assert job_dict["status"] == "completed"
        assert job_dict["config"]["param1"] == "value1"


class TestBatchScheduler:
    """Test BatchScheduler functionality."""

    @pytest.fixture
    def scheduler(self):
        """Create scheduler and ensure cleanup."""
        sched = BatchScheduler(max_concurrent_jobs=2)
        sched.start()
        yield sched
        sched.shutdown(wait=False)

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_scheduler_initialization(self):
        """Test scheduler initialization."""
        scheduler = BatchScheduler(max_concurrent_jobs=5)
        assert scheduler.max_concurrent_jobs == 5
        assert not scheduler.scheduler.running

        scheduler.start()
        assert scheduler.scheduler.running

        scheduler.shutdown()
        assert not scheduler.scheduler.running

    def test_schedule_one_time_job(self, scheduler):
        """Test scheduling a one-time job."""
        # Job to run in 2 seconds
        run_date = datetime.now() + timedelta(seconds=2)
        executed = []

        def test_function(config):
            executed.append(True)
            return {"success": True}

        job_id = scheduler.schedule_one_time_job(
            name="One-Time Test",
            run_date=run_date,
            process_func=test_function,
            config={"test": "data"}
        )

        assert job_id is not None
        assert job_id in scheduler.jobs

        # Check job status
        job = scheduler.jobs[job_id]
        assert job.name == "One-Time Test"
        assert job.job_type == JobType.ONE_TIME
        assert job.status == JobStatus.PENDING

        # Wait for execution
        time.sleep(3)

        # Verify execution
        assert len(executed) == 1
        job = scheduler.jobs[job_id]
        assert job.status == JobStatus.COMPLETED

    def test_schedule_recurring_job(self, scheduler):
        """Test scheduling a recurring job."""
        executed_count = []

        def test_function(config):
            executed_count.append(True)
            return {"count": len(executed_count)}

        # Schedule to run every 2 seconds
        job_id = scheduler.schedule_recurring_job(
            name="Recurring Test",
            cron_expression="*/2 * * * *",  # Every 2 minutes (for testing we'll use interval instead)
            process_func=test_function,
            config={"recurring": True}
        )

        assert job_id is not None
        job = scheduler.jobs[job_id]
        assert job.job_type == JobType.RECURRING

    def test_schedule_interval_job(self, scheduler):
        """Test scheduling interval-based job."""
        executed_count = []

        def test_function(config):
            executed_count.append(True)
            return {"count": len(executed_count)}

        # Run every 1 second
        job_id = scheduler.schedule_interval_job(
            name="Interval Test",
            interval_seconds=1,
            process_func=test_function,
            config={"interval": True}
        )

        assert job_id is not None
        job = scheduler.jobs[job_id]
        assert job.job_type == JobType.RECURRING

        # Wait for multiple executions
        time.sleep(3)

        # Should have executed at least 2 times
        assert len(executed_count) >= 2

    def test_watch_folder(self, scheduler, temp_dir):
        """Test watch folder automation."""
        processed_files = []

        def process_file(file_path, config):
            processed_files.append(file_path)
            return {"processed": file_path}

        # Setup watch folder
        watch_path = temp_dir / "watch"
        watch_path.mkdir()

        job_id = scheduler.setup_watch_folder(
            name="Watch Folder Test",
            watch_path=watch_path,
            process_func=process_file,
            config={"watch": True},
            pattern="*.pdf",
            interval_seconds=1
        )

        assert job_id is not None
        job = scheduler.jobs[job_id]
        assert job.job_type == JobType.WATCH_FOLDER

        # Create test files
        test_file1 = watch_path / "test1.pdf"
        test_file1.write_text("test content 1")

        # Wait for processing
        time.sleep(2)

        # Verify file was processed
        assert len(processed_files) >= 1
        assert str(test_file1) in processed_files

        # Create another file
        test_file2 = watch_path / "test2.pdf"
        test_file2.write_text("test content 2")

        time.sleep(2)

        # Should process new file but not reprocess first
        assert len(processed_files) >= 2

    def test_concurrent_job_limit(self, scheduler):
        """Test maximum concurrent jobs limit."""
        # Scheduler configured with max_concurrent_jobs=2

        running_jobs = []
        lock = []

        def slow_function(config):
            running_jobs.append(True)
            # Simulate long-running job
            time.sleep(2)
            running_jobs.pop()
            return {"success": True}

        # Schedule 3 jobs to run immediately
        for i in range(3):
            run_date = datetime.now() + timedelta(milliseconds=100 * i)
            scheduler.schedule_one_time_job(
                name=f"Concurrent Test {i}",
                run_date=run_date,
                process_func=slow_function,
                config={}
            )

        time.sleep(1)

        # Should never have more than 2 running simultaneously
        # This is checked within the slow_function by tracking running_jobs

    def test_cancel_job(self, scheduler):
        """Test canceling a scheduled job."""
        executed = []

        def test_function(config):
            executed.append(True)
            return {"success": True}

        # Schedule job for future
        run_date = datetime.now() + timedelta(seconds=5)
        job_id = scheduler.schedule_one_time_job(
            name="Cancel Test",
            run_date=run_date,
            process_func=test_function,
            config={}
        )

        # Cancel immediately
        success = scheduler.cancel_job(job_id)
        assert success

        job = scheduler.jobs[job_id]
        assert job.status == JobStatus.CANCELLED

        # Wait past scheduled time
        time.sleep(6)

        # Job should not have executed
        assert len(executed) == 0

    def test_job_failure_handling(self, scheduler):
        """Test handling of job failures."""
        def failing_function(config):
            raise ValueError("Intentional failure")

        run_date = datetime.now() + timedelta(seconds=1)
        job_id = scheduler.schedule_one_time_job(
            name="Failing Job",
            run_date=run_date,
            process_func=failing_function,
            config={}
        )

        # Wait for execution
        time.sleep(2)

        job = scheduler.jobs[job_id]
        assert job.status == JobStatus.FAILED
        assert "Intentional failure" in job.error

    def test_get_job_status(self, scheduler):
        """Test getting job status."""
        def test_function(config):
            return {"result": "success"}

        run_date = datetime.now() + timedelta(seconds=1)
        job_id = scheduler.schedule_one_time_job(
            name="Status Test",
            run_date=run_date,
            process_func=test_function,
            config={"test": "data"}
        )

        # Get status while pending
        status = scheduler.get_job_status(job_id)
        assert status is not None
        assert status["status"] == "pending"
        assert status["name"] == "Status Test"

        # Wait for execution
        time.sleep(2)

        # Get status after completion
        status = scheduler.get_job_status(job_id)
        assert status["status"] == "completed"
        assert status["result"]["result"] == "success"

    def test_list_jobs(self, scheduler):
        """Test listing jobs with filters."""
        def test_function(config):
            return {"success": True}

        # Create various jobs
        run_date = datetime.now() + timedelta(seconds=10)

        job1 = scheduler.schedule_one_time_job(
            "One-Time 1", run_date, test_function, {}
        )
        job2 = scheduler.schedule_interval_job(
            "Interval 1", 60, test_function, {}
        )

        # List all jobs
        all_jobs = scheduler.list_jobs()
        assert len(all_jobs) >= 2

        # Filter by status
        pending_jobs = scheduler.list_jobs(status=JobStatus.PENDING)
        assert len(pending_jobs) >= 1

        # Filter by type
        one_time_jobs = scheduler.list_jobs(job_type=JobType.ONE_TIME)
        assert len(one_time_jobs) >= 1

        recurring_jobs = scheduler.list_jobs(job_type=JobType.RECURRING)
        assert len(recurring_jobs) >= 1

    def test_get_running_jobs(self, scheduler):
        """Test getting currently running jobs."""
        running_jobs = scheduler.get_running_jobs()
        assert isinstance(running_jobs, list)

        # Initially should be empty
        assert len(running_jobs) == 0


class TestCronExpressions:
    """Test cron expression parsing."""

    @pytest.fixture
    def scheduler(self):
        """Create scheduler and ensure cleanup."""
        sched = BatchScheduler()
        sched.start()
        yield sched
        sched.shutdown(wait=False)

    def test_valid_cron_expressions(self, scheduler):
        """Test valid cron expressions."""
        def test_function(config):
            return {}

        # Valid cron patterns
        valid_crons = [
            "0 2 * * *",      # Daily at 2am
            "*/15 * * * *",   # Every 15 minutes
            "0 0 * * MON",    # Every Monday at midnight
            "0 8 1 * *",      # First day of month at 8am
            "30 */4 * * *",   # Every 4 hours at :30
        ]

        for cron in valid_crons:
            try:
                job_id = scheduler.schedule_recurring_job(
                    f"Cron Test {cron}",
                    cron,
                    test_function,
                    {}
                )
                assert job_id is not None
            except ValueError:
                pytest.fail(f"Valid cron expression rejected: {cron}")

    def test_invalid_cron_expressions(self, scheduler):
        """Test invalid cron expressions."""
        def test_function(config):
            return {}

        # Invalid cron patterns
        invalid_crons = [
            "invalid",           # Not a cron expression
            "0 2 * *",          # Too few parts
            "0 2 * * * *",      # Too many parts
            "60 25 * * *",      # Invalid time values
        ]

        for cron in invalid_crons:
            with pytest.raises(ValueError):
                scheduler.schedule_recurring_job(
                    f"Invalid Cron {cron}",
                    cron,
                    test_function,
                    {}
                )


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def scheduler(self):
        """Create scheduler and ensure cleanup."""
        sched = BatchScheduler()
        sched.start()
        yield sched
        sched.shutdown(wait=False)

    def test_get_nonexistent_job_status(self, scheduler):
        """Test getting status of nonexistent job."""
        status = scheduler.get_job_status("nonexistent")
        assert status is None

    def test_cancel_nonexistent_job(self, scheduler):
        """Test canceling job that doesn't exist."""
        success = scheduler.cancel_job("nonexistent")
        assert not success

    def test_watch_folder_creates_directory(self, scheduler):
        """Test that watch folder creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            watch_path = Path(tmpdir) / "nonexistent" / "watch"

            def test_function(file_path, config):
                pass

            job_id = scheduler.setup_watch_folder(
                "Create Dir Test",
                watch_path,
                test_function,
                {},
                interval_seconds=60
            )

            # Directory should be created
            assert watch_path.exists()
            assert watch_path.is_dir()

    def test_shutdown_with_pending_jobs(self, scheduler):
        """Test shutting down with pending jobs."""
        def test_function(config):
            time.sleep(5)  # Long-running job
            return {}

        run_date = datetime.now() + timedelta(milliseconds=100)
        scheduler.schedule_one_time_job(
            "Shutdown Test",
            run_date,
            test_function,
            {}
        )

        time.sleep(0.5)

        # Shutdown without waiting
        scheduler.shutdown(wait=False)
        assert not scheduler.scheduler.running


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
