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
        
        # 앱 시작 시 폰트 로딩 문제로 멈추는 것을 방지하기 위해 기본 폰트 사용
        # page.fonts 제거
        
        # 저장 경로 설정
        download_path = "/storage/emulated/0/Download/InstaSave"
        if os.name == 'nt':
            download_path = os.path.join(os.getcwd(), "downloads")
            
        downloader = InstaDownloader(download_dir=download_path)

        # UI 컴포넌트 생성 (기존과 동일하되 더 안전하게)
        header = ft.Column(
            [
                ft.Icon(name=ft.icons.INSTAGRAM, size=60, color=ft.colors.PINK_400),
                ft.Text("Insta Save Pro", size=32, weight=ft.FontWeight.BOLD, color=ft.colors.WHITE),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        url_input = ft.TextField(
            label="Instagram URL",
            border_radius=15,
            bgcolor=ft.colors.with_opacity(0.1, ft.colors.WHITE),
            expand=True
        )

        prog_bar = ft.ProgressBar(visible=False, color=ft.colors.PINK_400)
        status_text = ft.Text("", size=12)
        log_area = ft.ListView(expand=True, spacing=5, height=150)

        async def start_download(e):
            if not url_input.value: return
            prog_bar.visible = True
            page.update()
            success, result = await asyncio.to_thread(downloader.parse_url_and_download, url_input.value)
            prog_bar.visible = False
            status_text.value = "완료!" if success else f"실패: {result}"
            page.update()

        btn_download = ft.ElevatedButton(
            "DOWNLOAD", 
            on_click=start_download,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=15))
        )

        page.add(header, url_input, btn_download, prog_bar, status_text, log_area)
        
    except Exception as e:
        # 오류 발생 시 화면에 표시
        page.add(ft.Text(f"App Start Error: {str(e)}", color="red"))
        page.update()

if __name__ == "__main__":
    ft.app(target=main)

