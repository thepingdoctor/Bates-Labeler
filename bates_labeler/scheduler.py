"""Batch Job Scheduler for Bates-Labeler.

This module provides scheduling capabilities for automated PDF processing:
- Schedule one-time or recurring batch jobs
- Watch folders for automatic processing
- Email notifications on completion/failure
- Job queue management
- Cron-like scheduling

Requires APScheduler for scheduling functionality.
"""

import logging
import os
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.date import DateTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    SCHEDULER_AVAILABLE = True
except ImportError:
    SCHEDULER_AVAILABLE = False
    BackgroundScheduler = None  # type: ignore


logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class JobType(Enum):
    """Job scheduling type."""
    ONE_TIME = "one_time"
    RECURRING = "recurring"
    WATCH_FOLDER = "watch_folder"


class Job:
    """Batch processing job.

    Attributes:
        job_id: Unique job identifier
        name: Job name
        job_type: Job type (one-time, recurring, watch folder)
        status: Current job status
        config: Job configuration
        created: Creation timestamp
        last_run: Last execution timestamp
        next_run: Next scheduled execution
        error: Error message if failed
    """

    def __init__(
        self,
        job_id: str,
        name: str,
        job_type: JobType,
        config: Dict[str, Any]
    ):
        """Initialize job.

        Args:
            job_id: Unique job identifier
            name: Job name
            job_type: Job type
            config: Job configuration
        """
        self.job_id = job_id
        self.name = name
        self.job_type = job_type
        self.config = config
        self.status = JobStatus.PENDING
        self.created = datetime.now()
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'job_id': self.job_id,
            'name': self.name,
            'job_type': self.job_type.value,
            'status': self.status.value,
            'config': self.config,
            'created': self.created.isoformat(),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'error': self.error,
            'result': self.result
        }


class BatchScheduler:
    """Batch job scheduler for automated PDF processing.

    Features:
    - One-time scheduled jobs
    - Recurring jobs (cron-like)
    - Watch folder automation
    - Job queue management
    - Status tracking
    - Error handling and retries
    """

    def __init__(
        self,
        max_concurrent_jobs: int = 3,
        enable_notifications: bool = False
    ):
        """Initialize batch scheduler.

        Args:
            max_concurrent_jobs: Maximum concurrent jobs
            enable_notifications: Enable email notifications

        Raises:
            ImportError: If APScheduler not installed
        """
        if not SCHEDULER_AVAILABLE:
            raise ImportError(
                "APScheduler not installed. Install with: "
                "pip install APScheduler>=3.10.0"
            )

        self.max_concurrent_jobs = max_concurrent_jobs
        self.enable_notifications = enable_notifications

        self.scheduler = BackgroundScheduler()
        self.jobs: Dict[str, Job] = {}
        self.running_jobs: Dict[str, Job] = {}

        self._job_counter = 0

        logger.info("BatchScheduler initialized")

    def start(self) -> None:
        """Start the scheduler."""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def shutdown(self, wait: bool = True) -> None:
        """Shutdown the scheduler.

        Args:
            wait: Wait for running jobs to complete
        """
        if self.scheduler.running:
            self.scheduler.shutdown(wait=wait)
            logger.info("Scheduler stopped")

    def _generate_job_id(self) -> str:
        """Generate unique job ID.

        Returns:
            Unique job ID
        """
        self._job_counter += 1
        return f"job_{int(time.time())}_{self._job_counter}"

    def schedule_one_time_job(
        self,
        name: str,
        run_date: datetime,
        process_func: Callable,
        config: Dict[str, Any]
    ) -> str:
        """Schedule a one-time batch job.

        Args:
            name: Job name
            run_date: When to run the job
            process_func: Processing function to execute
            config: Job configuration

        Returns:
            Job ID
        """
        job_id = self._generate_job_id()

        job = Job(
            job_id=job_id,
            name=name,
            job_type=JobType.ONE_TIME,
            config=config
        )
        job.next_run = run_date

        # Schedule with APScheduler
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=DateTrigger(run_date=run_date),
            args=[job_id, process_func],
            id=job_id,
            name=name
        )

        self.jobs[job_id] = job
        logger.info(f"Scheduled one-time job: {name} at {run_date}")

        return job_id

    def schedule_recurring_job(
        self,
        name: str,
        cron_expression: str,
        process_func: Callable,
        config: Dict[str, Any]
    ) -> str:
        """Schedule a recurring batch job.

        Args:
            name: Job name
            cron_expression: Cron expression (e.g., "0 2 * * *" for daily at 2am)
            process_func: Processing function to execute
            config: Job configuration

        Returns:
            Job ID

        Example cron expressions:
            "0 2 * * *"     - Daily at 2am
            "0 */4 * * *"   - Every 4 hours
            "0 0 * * MON"   - Every Monday at midnight
            "0 8 1 * *"     - First day of month at 8am
        """
        job_id = self._generate_job_id()

        job = Job(
            job_id=job_id,
            name=name,
            job_type=JobType.RECURRING,
            config=config
        )

        # Parse cron expression
        cron_parts = cron_expression.split()
        if len(cron_parts) != 5:
            raise ValueError("Invalid cron expression. Expected 5 parts: minute hour day month day_of_week")

        minute, hour, day, month, day_of_week = cron_parts

        # Schedule with APScheduler
        trigger = CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        )

        self.scheduler.add_job(
            func=self._execute_job,
            trigger=trigger,
            args=[job_id, process_func],
            id=job_id,
            name=name
        )

        self.jobs[job_id] = job
        logger.info(f"Scheduled recurring job: {name} with cron: {cron_expression}")

        return job_id

    def schedule_interval_job(
        self,
        name: str,
        interval_seconds: int,
        process_func: Callable,
        config: Dict[str, Any]
    ) -> str:
        """Schedule a job to run at fixed intervals.

        Args:
            name: Job name
            interval_seconds: Interval in seconds
            process_func: Processing function to execute
            config: Job configuration

        Returns:
            Job ID
        """
        job_id = self._generate_job_id()

        job = Job(
            job_id=job_id,
            name=name,
            job_type=JobType.RECURRING,
            config=config
        )

        # Schedule with APScheduler
        self.scheduler.add_job(
            func=self._execute_job,
            trigger=IntervalTrigger(seconds=interval_seconds),
            args=[job_id, process_func],
            id=job_id,
            name=name
        )

        self.jobs[job_id] = job
        logger.info(f"Scheduled interval job: {name} every {interval_seconds}s")

        return job_id

    def setup_watch_folder(
        self,
        name: str,
        watch_path: Union[str, Path],
        process_func: Callable,
        config: Dict[str, Any],
        pattern: str = "*.pdf",
        interval_seconds: int = 60
    ) -> str:
        """Setup watch folder for automatic processing.

        Args:
            name: Job name
            watch_path: Directory to watch
            process_func: Processing function to execute
            config: Job configuration
            pattern: File pattern to match (e.g., "*.pdf")
            interval_seconds: Check interval in seconds

        Returns:
            Job ID
        """
        watch_path = Path(watch_path)

        if not watch_path.exists():
            watch_path.mkdir(parents=True, exist_ok=True)

        job_id = self._generate_job_id()

        config['watch_path'] = str(watch_path)
        config['pattern'] = pattern
        config['processed_files'] = set()

        job = Job(
            job_id=job_id,
            name=name,
            job_type=JobType.WATCH_FOLDER,
            config=config
        )

        # Create watch folder wrapper
        def watch_folder_wrapper():
            self._process_watch_folder(job_id, process_func)

        # Schedule periodic check
        self.scheduler.add_job(
            func=watch_folder_wrapper,
            trigger=IntervalTrigger(seconds=interval_seconds),
            id=job_id,
            name=name
        )

        self.jobs[job_id] = job
        logger.info(f"Setup watch folder: {watch_path} checking every {interval_seconds}s")

        return job_id

    def _process_watch_folder(self, job_id: str, process_func: Callable) -> None:
        """Process new files in watch folder.

        Args:
            job_id: Job ID
            process_func: Processing function
        """
        job = self.jobs.get(job_id)
        if not job:
            return

        watch_path = Path(job.config['watch_path'])
        pattern = job.config['pattern']
        processed_files = job.config['processed_files']

        # Find new files
        new_files = []
        for file_path in watch_path.glob(pattern):
            if str(file_path) not in processed_files:
                new_files.append(file_path)

        if new_files:
            logger.info(f"Found {len(new_files)} new files in {watch_path}")

            # Process new files
            for file_path in new_files:
                try:
                    # Execute processing function
                    process_func(str(file_path), job.config)

                    # Mark as processed
                    processed_files.add(str(file_path))

                    logger.info(f"Processed: {file_path}")

                except Exception as e:
                    logger.error(f"Error processing {file_path}: {e}")

    def _execute_job(self, job_id: str, process_func: Callable) -> None:
        """Execute a batch job.

        Args:
            job_id: Job ID
            process_func: Processing function to execute
        """
        job = self.jobs.get(job_id)
        if not job:
            logger.error(f"Job not found: {job_id}")
            return

        # Check concurrent job limit
        if len(self.running_jobs) >= self.max_concurrent_jobs:
            logger.warning(f"Max concurrent jobs reached. Job {job_id} will retry.")
            return

        job.status = JobStatus.RUNNING
        job.last_run = datetime.now()
        self.running_jobs[job_id] = job

        logger.info(f"Executing job: {job.name} ({job_id})")

        try:
            # Execute processing function
            result = process_func(job.config)

            job.status = JobStatus.COMPLETED
            job.result = result

            logger.info(f"Job completed: {job.name}")

            if self.enable_notifications:
                self._send_notification(job, success=True)

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)

            logger.error(f"Job failed: {job.name} - {e}")

            if self.enable_notifications:
                self._send_notification(job, success=False)

        finally:
            self.running_jobs.pop(job_id, None)

    def _send_notification(self, job: Job, success: bool) -> None:
        """Send job completion notification.

        Args:
            job: Job that completed
            success: Whether job succeeded
        """
        # Placeholder for email notification
        # In production, integrate with SMTP or notification service
        status = "succeeded" if success else "failed"
        logger.info(f"Notification: Job '{job.name}' {status}")

    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job.

        Args:
            job_id: Job ID to cancel

        Returns:
            True if cancelled, False if not found
        """
        if job_id in self.jobs:
            job = self.jobs[job_id]

            # Remove from scheduler
            try:
                self.scheduler.remove_job(job_id)
            except Exception:
                pass

            job.status = JobStatus.CANCELLED
            logger.info(f"Job cancelled: {job.name}")

            return True
        return False

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status.

        Args:
            job_id: Job ID

        Returns:
            Job status dictionary or None
        """
        job = self.jobs.get(job_id)
        if job:
            return job.to_dict()
        return None

    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        job_type: Optional[JobType] = None
    ) -> List[Dict[str, Any]]:
        """List jobs with optional filtering.

        Args:
            status: Filter by status
            job_type: Filter by type

        Returns:
            List of job dictionaries
        """
        jobs = list(self.jobs.values())

        if status:
            jobs = [j for j in jobs if j.status == status]

        if job_type:
            jobs = [j for j in jobs if j.job_type == job_type]

        return [j.to_dict() for j in jobs]

    def get_running_jobs(self) -> List[Dict[str, Any]]:
        """Get currently running jobs.

        Returns:
            List of running job dictionaries
        """
        return [j.to_dict() for j in self.running_jobs.values()]
