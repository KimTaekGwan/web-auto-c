"""
캡처 작업 큐 관리
"""

import os
import time
import queue
import threading
from typing import List, Dict, Any, Callable, Optional

from ..config.config import logger
from ..models.models import DeviceType, CaptureResult, PageCapture


class CaptureTask:
    """캡처 작업 정의"""

    def __init__(self, url: str, device_type: DeviceType, output_dir: str):
        self.url = url
        self.device_type = device_type
        self.output_dir = output_dir
        self.timestamp = time.time()


class CaptureQueue:
    """캡처 작업 큐"""

    def __init__(self, max_workers: int = 3):
        self.queue = queue.Queue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        self.result = CaptureResult()
        self.lock = threading.Lock()

    def add_task(self, task: CaptureTask):
        """큐에 작업 추가"""
        self.queue.put(task)
        logger.debug(f"작업 추가: {task.url} ({task.device_type})")

    def add_tasks_from_urls(
        self, urls: List[str], device_types: List[DeviceType], output_dir: str
    ):
        """URL 목록에서 작업 추가"""
        for url in urls:
            for device_type in device_types:
                self.add_task(CaptureTask(url, device_type, output_dir))

        logger.info(f"{len(urls) * len(device_types)}개 작업 추가 완료")

    def add_capture_result(self, capture: PageCapture):
        """캡처 결과 추가 (스레드 안전)"""
        with self.lock:
            self.result.add_capture(capture)

    def _worker(
        self,
        worker_id: int,
        process_func: Callable[[CaptureTask], Optional[PageCapture]],
    ):
        """작업자 스레드"""
        logger.info(f"작업자 {worker_id} 시작")

        while self.running:
            try:
                # 큐에서 작업 가져오기 (1초 타임아웃)
                task = self.queue.get(timeout=1)

                # 작업 처리
                logger.debug(
                    f"작업자 {worker_id}가 작업 처리 중: {task.url} ({task.device_type})"
                )
                try:
                    capture_result = process_func(task)
                    if capture_result:
                        self.add_capture_result(capture_result)
                except Exception as e:
                    logger.error(f"작업자 {worker_id} 오류: {str(e)}")

                # 작업 완료 표시
                self.queue.task_done()

            except queue.Empty:
                pass  # 큐가 비어있으면 계속 진행

        logger.info(f"작업자 {worker_id} 종료")

    def start(self, process_func: Callable[[CaptureTask], Optional[PageCapture]]):
        """작업 큐 시작"""
        if self.running:
            logger.warning("작업 큐가 이미 실행 중입니다.")
            return

        self.running = True
        self.result = CaptureResult()

        # 작업자 시작
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker, args=(i + 1, process_func))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)

        logger.info(f"{self.max_workers}개 작업자 시작")

    def stop(self):
        """작업 큐 중지"""
        logger.info("작업 큐 중지 중...")
        self.running = False

        # 모든 작업자 종료 대기
        for worker in self.workers:
            worker.join(timeout=5)

        self.workers = []

        # 결과 완료 처리
        self.result.complete()
        logger.info(
            f"작업 큐 중지 완료 (성공: {self.result.success_count}, 실패: {self.result.error_count})"
        )

    def wait(self, timeout: Optional[float] = None):
        """모든 작업 완료까지 대기"""
        try:
            self.queue.join()
            logger.info("모든 작업 완료")
            return True
        except KeyboardInterrupt:
            logger.warning("작업 중단됨")
            return False
