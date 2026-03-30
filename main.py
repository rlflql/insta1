import flet as ft
import os
import asyncio
from insta_logic import InstaDownloader

async def main(page: ft.Page):
    try:
        # 페이지 기본 설정
        page.title = "Insta Save Pro"
        page.theme_mode = ft.ThemeMode.DARK
        page.padding = 20
        page.bgcolor = "#0F0F1A"
        
        # 저장 경로 설정
        download_path = "/storage/emulated/0/Download/InstaSave"
        if os.name == 'nt':
            download_path = os.path.join(os.getcwd(), "downloads")
            
        downloader = InstaDownloader(download_dir=download_path)

        # --- UI 컴포넌트 ---
        
        # 상단 로고 (이름을 명시하지 않고 "camera" 문자열만 전달)
        header = ft.Column(
            [
                ft.Icon("camera", size=60, color="pink400"),
                ft.Text("Insta Save Pro", size=32, weight="bold", color="white"),
                ft.Text("Original Quality Downloader", size=14, color="grey400"),
            ],
            horizontal_alignment="center",
        )

        # URL 입력창
        url_input = ft.TextField(
            label="Instagram URL",
            hint_text="주소를 입력하세요",
            border_radius=15,
            border_color="pink300",
            # prefix_icon도 문자열로 직접 전달
            prefix_icon="link",
            expand=True
        )

        prog_bar = ft.ProgressBar(width=400, color="pink400", visible=False)
        status_text = ft.Text("", size=12, color="grey400")
        log_area = ft.ListView(expand=True, spacing=5, height=150)

        def add_log(msg, is_error=False):
            log_area.controls.append(
                ft.Text(f"• {msg}", color="red400" if is_error else "green200", size=12)
            )
            page.update()

        async def start_download(e):
            url = url_input.value.strip()
            if not url: return

            btn_download.disabled = True
            prog_bar.visible = True
            status_text.value = "이미지 분석 중..."
            page.update()

            # 실제 다운로드 실행
            success, result = await asyncio.to_thread(downloader.parse_url_and_download, url)
            
            btn_download.disabled = False
            prog_bar.visible = False
            status_text.value = "완료" if success else "실패"
            
            if success:
                add_log(f"성공: {len(result)}개 파일 저장")
            else:
                add_log(str(result), is_error=True)
            page.update()

        # 다운로드 버튼
        btn_download = ft.Container(
            content=ft.Text("DOWNLOAD", weight="bold", color="white"),
            alignment=ft.alignment.center,
            padding=15,
            border_radius=15,
            gradient=ft.LinearGradient(colors=["pink500", "purple600"]),
            on_click=start_download,
        )

        # 로그인 섹션
        def show_login(e):
            bs.open = True
            page.update()

        login_user = ft.TextField(label="Username")
        login_pass = ft.TextField(label="Password", password=True)

        bs = ft.BottomSheet(
            ft.Container(
                ft.Column([
                    ft.Text("Login Settings", size=20, weight="bold"),
                    login_user, login_pass,
                    ft.ElevatedButton("Save", on_click=lambda _: None) 
                ], tight=True),
                padding=20, bgcolor="#161625"
            )
        )
        page.overlay.append(bs)

        # 전체 화면 구성
        page.add(
            ft.Column(
                [
                    header,
                    ft.Divider(height=20, color="transparent"),
                    url_input,
                    btn_download,
                    prog_bar,
                    status_text,
                    log_area,
                    # Icon 명칭 미사용 버전
                    ft.ListTile(leading=ft.Icon("lock"), title=ft.Text("Login Settings"), on_click=show_login)
                ],
                horizontal_alignment="center",
            )
        )
        
    except Exception as e:
        # 모든 오류를 텍스트로 안전하게 출력
        page.add(ft.Text(f"Critical Runtime Error: {str(e)}", color="red"))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
