import os
import re
import datetime
import subprocess
from pathlib import Path
import instaloader

class InstaDownloader:
    def __init__(self, download_dir="downloads"):
        self.L = instaloader.Instaloader(
            download_pictures=True,
            download_videos=True,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            post_metadata_txt_pattern="",
            dirname_pattern=download_dir
        )
        self.download_dir = Path(download_dir)
        
        # [수정] 안드로이드 호환성을 위해 ZoneInfo 대신 고정 오프셋 사용
        self.kst = datetime.timezone(datetime.timedelta(hours=9))
        self.session_file = "insta_session"

    def login(self, username, password):
        """인스타그램 로그인 (세션 저장)"""
        try:
            self.L.login(username, password)
            self.L.save_session_to_file(self.session_file)
            return True, "로그인 성공"
        except Exception as e:
            return False, f"로그인 실패: {str(e)}"

    def load_session(self, username):
        """저장된 세션 불러오기"""
        try:
            self.L.load_session_from_file(username, self.session_file)
            return True
        except:
            return False

    def get_kst_time(self, utc_time):
        """UTC 시간을 KST(한국 시간)으로 변환"""
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=datetime.timezone.utc)
        return utc_time.astimezone(self.kst)

    def clean_filename(self, filename):
        """파일명에 사용 불가능한 문자 제거"""
        return re.sub(r'[\/:*?"<>|]', '_', filename)

    def download_post(self, url, progress_callback=None):
        """일반 게시물(Post/Reel) 다운로드"""
        try:
            match = re.search(r'/(?:p|reels|reel)/([^/?#&]+)', url)
            if not match:
                return False, "올바른 게시물 URL이 아닙니다."
            
            shortcode = match.group(1)
            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            
            kst_date = self.get_kst_time(post.date_utc)
            base_filename = kst_date.strftime("%y%m%d %H시 %M분")
            
            save_path = self.download_dir
            save_path.mkdir(parents=True, exist_ok=True)

            nodes = list(post.get_sidecar_nodes()) if post.typename == 'GraphSidecar' else [post]
            count = len(nodes)
            
            downloaded_files = []
            for i, node in enumerate(nodes, 1):
                suffix = f"_{i}" if count > 1 else ""
                final_filename = f"{base_filename}{suffix}"
                
                target_url = node.video_url if node.is_video else node.display_url
                extension = "mp4" if node.is_video else "jpg"
                file_path = save_path / f"{final_filename}.{extension}"
                
                self.L.download_pic(file_path, target_url, post.date_utc)
                downloaded_files.append(str(file_path))
                
                self.scan_media(file_path)

                if progress_callback:
                    progress_callback(i / count, f"{i}/{count} 완료")

            return True, downloaded_files
        except Exception as e:
            return False, f"다운로드 오류: {str(e)}"

    def scan_media(self, file_path):
        """안드로이드 미디어 스캐너 호출 (갤러리 즉시 반영)"""
        if os.name != 'nt':
            try:
                subprocess.run(['am', 'broadcast', '-a', 'android.intent.action.MEDIA_SCANNER_SCAN_FILE', '-d', f'file://{file_path}'], capture_output=True)
            except:
                pass

    def download_stories(self, username, progress_callback=None):
        """사용자의 모든 스토리 다운로드"""
        try:
            profile = instaloader.Profile.from_username(self.L.context, username)
            stories = self.L.get_stories(userids=[profile.userid])
            
            downloaded_files = []
            all_items = []
            for story in stories:
                for item in story.get_items():
                    all_items.append(item)
            
            total = len(all_items)
            if total == 0:
                return False, "현재 다운로드 가능한 스토리가 없습니다."

            all_items.sort(key=lambda x: x.date_utc)
            time_counts = {}

            for i, item in enumerate(all_items, 1):
                kst_date = self.get_kst_time(item.date_utc)
                time_key = kst_date.strftime("%y%m%d %H시 %M분 %S초")
                
                if time_key in time_counts:
                    time_counts[time_key] += 1
                    final_filename = f"{kst_date.strftime('%y%m%d %H시 %M분')}_{time_counts[time_key]}"
                else:
                    time_counts[time_key] = 1
                    final_filename = time_key
                
                save_path = self.download_dir
                save_path.mkdir(parents=True, exist_ok=True)
                
                target_url = item.video_url if item.is_video else item.display_url
                extension = "mp4" if item.is_video else "jpg"
                file_path = save_path / f"{final_filename}.{extension}"
                
                self.L.download_pic(file_path, target_url, item.date_utc)
                downloaded_files.append(str(file_path))
                self.scan_media(file_path)

                if progress_callback:
                    progress_callback(i / total, f"{i}/{total} 스토리 완료")

            return True, downloaded_files
        except Exception as e:
            return False, f"스토리 다운로드 오류: {str(e)}"

    def parse_url_and_download(self, url, progress_callback=None):
        """URL 유형 분석 후 적절한 함수 실행"""
        if "stories/" in url:
            match = re.search(r'stories/([^/?#&]+)', url)
            if match:
                return self.download_stories(match.group(1), progress_callback)
        return self.download_post(url, progress_callback)
