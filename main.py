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
        page.bgcolor = "#0F0F1A" # 딥 네이비 블랙
        
        # 저장 경로 설정 (안드로이드/PC 구분)
        download_path = "/storage/emulated/0/Download/InstaSave"
        if os.name == 'nt':
            download_path = os.path.join(os.getcwd(), "downloads")
            
        downloader = InstaDownloader(download_dir=download_path)

        # --- UI 컴포넌트 ---
        
        # 상단 로고 (INSTAGRAM -> CAMERA_ALT로 변경하여 오류 방지)
        header = ft.Column(
            [
                ft.Icon(name=ft.icons.CAMERA_ALT, size=60, color=ft.colors.PINK_400),
                ft.Text("Insta Save Pro", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
                ft.Text("Original Quality Downloader", size=14, color=ft.colors.GREY_400),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        # URL 입력창
        url_input = ft.TextField(
            label="Instagram URL",
            hint_text="게시물 또는 스토리 주소를 입력하세요",
            border_radius=15,
            border_color=ft.colors.PINK_300,
            focused_border_color=ft.colors.PINK_500,
            prefix_icon=ft.icons.LINK,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            expand=True
        )

        # 진행바 및 상태 메시지
        prog_bar = ft.ProgressBar(width=400, color=ft.colors.PINK_400, bgcolor="#1A1A2E", value=0, visible=False)
        status_text = ft.Text("", size=12, color=ft.colors.GREY_400)
        log_area = ft.ListView(expand=True, spacing=5, padding=10, height=150)

        def add_log(msg, is_error=False):
            log_area.controls.append(
                ft.Text(f"• {msg}", color=ft.colors.RED_400 if is_error else ft.colors.GREEN_200, size=12)
            )
            page.update()

        async def start_download(e):
            url = url_input.value.strip()
            if not url:
                page.show_snack_bar(ft.SnackBar(ft.Text("URL을 입력해 주세요!")))
                return

            btn_download.disabled = True
            prog_bar.visible = True
            prog_bar.value = None
            status_text.value = "이미지/영상 분석 중..."
            page.update()

            def update_progress(ratio, text):
                prog_bar.value = ratio
                status_text.value = text
                page.update()

            # 실제 다운로드 실행
            success, result = await asyncio.to_thread(downloader.parse_url_and_download, url, update_progress)
            
            btn_download.disabled = False
            prog_bar.visible = False
            
            if success:
                add_log(f"성공: {len(result)}개 파일 저장 완료")
                status_text.value = "다운로드 완료!"
            else:
                add_log(str(result), is_error=True)
                status_text.value = "다운로드 실패"
            
            page.update()

        # 다운로드 버튼
        btn_download = ft.Container(
            content=ft.Text("DOWNLOAD", weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            alignment=ft.alignment.center,
            padding=15,
            border_radius=15,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_left,
                end=ft.alignment.bottom_right,
                colors=[ft.colors.PINK_500, ft.colors.PURPLE_600]
            ),
            on_click=start_download,
            ink=True
        )

        # --- 로그인 관리 (비공개 계정용) ---
        login_user = ft.TextField(label="Username", border_radius=10)
        login_pass = ft.TextField(label="Password", password=True, can_reveal_password=True, border_radius=10)

        def handle_login(e):
            if not login_user.value or not login_pass.value: return
            success, msg = downloader.login(login_user.value, login_pass.value)
            if success:
                add_log("로그인 성공!")
                bs.open = False
            else:
                add_log(msg, is_error=True)
            page.update()

        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Text("Instagram Login", size=20, weight=ft.FontWeight.BOLD),
                        login_user, login_pass,
                        ft.ElevatedButton("Login", on_click=handle_login, bgcolor=ft.colors.PINK_600, color=ft.colors.WHITE),
                    ],
                    tight=True, spacing=15, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=30, bgcolor="#161625", border_radius=ft.border_radius.only(top_left=20, top_right=20)
            )
        )
        page.overlay.append(bs)

        # 레이아웃 구성
        page.add(
            ft.Container(
                content=ft.Column(
                    [
                        header,
                        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                        ft.Row([url_input]),
                        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                        btn_download,
                        prog_bar,
                        status_text,
                        ft.Divider(height=20, color=ft.colors.TRANSPARENT),
                        ft.Text("Recent Logs", size=14, weight=ft.FontWeight.BOLD),
                        ft.Container(content=log_area, bgcolor=ft.colors.with_opacity(0.05, ft.colors.WHITE), border_radius=10),
                        ft.Divider(height=10, color=ft.colors.TRANSPARENT),
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.LOCK),
                            title=ft.Text("로그인 설정 (비공개 계정용)"),
                            on_click=lambda _: setattr(bs, "open", True) or page.update()
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                expand=True
            )
        )
        
    except Exception as e:
        page.add(ft.Text(f"App Start Error: {str(e)}", color="red"))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
