from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu
from PySide6.QtGui import QPixmap, QMouseEvent, QCursor, QAction, QMovie
from PySide6.QtCore import Qt, QPoint
from widgets import (
    emoji_selecter, 
    video_download_widget,
    blivedm_widget,
    bulletscreen_player,
    bulletscreen_widget,
    setting_page_vibe_c, 
)

class AnimatedImageWidget(QWidget):
    def __init__(self, image_path: str, parent=None):
        super().__init__(parent)

        # 窗口基础配置
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 图片显示控件
        self.imageLabel = QLabel()
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setAttribute(Qt.WA_TranslucentBackground)

        self.movie = None  # 存储 GIF 播放对象
        self.isGif = False  # 标记是否是 GIF

        # 加载图片/GIF
        self._loadAnimatedImage(image_path)

        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.imageLabel)

        # 初始化控件右键菜单（仅保留隐藏到托盘）
        self._rightMenu = None
        self._initRightMenu()

        # 拖拽变量
        self._offsetPos = QPoint()

        self.adjustSize()

        self._emojiSelecter : emoji_selecter.emoSearchListWidget | None = None
        self._videoDownloadWidget : video_download_widget.vdoDownWidget | None = None
        self._blivedmWidget : blivedm_widget.blivedmObject | None = None
        self._bulletscreenPlayer : bulletscreen_player.bulletscreenObject | None = None
        self._bulletscreenWidget : bulletscreen_widget.bullscrContainer | None = None
        self._settingPageWidget : setting_page_vibe_c.settingPage | None = None

    def _initRightMenu(self):
        self._rightMenu = QMenu(self)
        self._rightMenu.setObjectName("WidgetMenu")

        self._rightMenu.setStyleSheet("""
            QMenu#WidgetMenu {
                /* 1. 背景与边框：使用系统调色板，完美适配明/暗模式 */
                background-color: palette(window);
                border: 1px solid palette(mid);
                
                /* 2. 圆角：适度的4px圆角，既现代又不会触发过多抗锯齿计算 */
                border-radius: 4px;
                
                /* 3. 菜单内边距：给圆角留出空间，防止选项顶格 */
                padding: 4px;
                
                /* 性能提示：避免使用box-shadow或复杂的background-image，这会显著提升首次加载速度 */
            }

            QMenu#WidgetMenu::item {
                /* 4. 选项间距：优化左右内边距
                Fusion风格默认左侧预留了图标位，导致文字偏右。
                这里统一缩小内边距，在视觉上平衡左右 */
                padding: 7px 14px; 
                margin: 0px;        /* 去除选项间的外边距，使选中块连贯 */
                
                /* 5. 轻量圆角：仅3px，减少绘制开销 */
                border-radius: 3px; 
            }

            QMenu#WidgetMenu::item:selected {
                /* 6. 选中态：纯色填充，无渐变，最快渲染速度 */
                background-color: palette(highlight);
                color: palette(highlightedText);
                border-radius: 3px;
            }
    
            /* 7. 分隔线优化：让分隔线更精致 */
            QMenu#WidgetMenu::separator {
                height: 1px;
                background: palette(mid);
                margin: 4px 10px; /* 缩短分隔线长度，增加留白 */
            }
        """)

        self.hide_to_tray_action = QAction("隐藏界面", self)
        self.hide_to_tray_action.triggered.connect(self.hideToTray)
        self._rightMenu.addAction(self.hide_to_tray_action)

        self._rightMenu.addSeparator()

        emojiDownloadAction = QAction("下载表情包", self._rightMenu)
        emojiDownloadAction.triggered.connect(self.emojiDownload)
        self._rightMenu.addAction(emojiDownloadAction)

        vdoDownloadAction = QAction("下载BV视频", self._rightMenu)
        vdoDownloadAction.triggered.connect(self.vdoDownload)
        self._rightMenu.addAction(vdoDownloadAction)

        self._rightMenu.addSeparator()

        dmPlayerAction = QAction("语音弹幕", self._rightMenu)
        dmPlayerAction.setCheckable(True)
        dmPlayerAction.triggered.connect(self.onDmPlayer)
        self._rightMenu.addAction(dmPlayerAction)

        dmWidgetAction = QAction("桌面弹幕", self._rightMenu)
        dmWidgetAction.setCheckable(True)
        dmWidgetAction.triggered.connect(self.onDmWidget)
        self._rightMenu.addAction(dmWidgetAction)

        self._rightMenu.addSeparator()

        settingPageAcion = QAction("设置页面", self._rightMenu)
        settingPageAcion.triggered.connect(self.openSettingPage)
        self._rightMenu.addAction(settingPageAcion)

        self._rightMenu.addSeparator()

        self.quitAppAction = QAction("退出应用", self)
        self.quitAppAction.triggered.connect(lambda: QApplication.quit())
        self._rightMenu.addAction(self.quitAppAction)

    # ========== 修改2：优化load_image函数，支持动态切换图片/GIF ==========
    def _loadAnimatedImage(self, image_path: str):
        """加载/切换图片/GIF（优化后支持动态切换，避免控件异常）"""
        if not Path(image_path).exists():
            print(f"错误：图片路径 {image_path} 不存在")
            self.isGif = False
            return

        # 1. 清理原有资源（关键：切换前释放旧的图片/GIF资源）
        if self.isGif and self.movie:
            # 停止并释放原有GIF
            self.movie.stop()
            self.movie.frameChanged.disconnect()  # 断开所有信号连接
            self.movie.deleteLater()  # 释放资源
            self.movie = None
        # 清空Label内容
        self.imageLabel.clear()

        # 3. 判断是否是 GIF
        suffix = Path(image_path).suffix.lower()
        if suffix in [".gif", ".GIF"]:
            self.isGif = True
            # 创建 QMovie 加载 GIF
            self.movie = QMovie(image_path)

            # 监听 GIF 帧加载完成信号，再设置尺寸
            self.movie.frameChanged.connect(self._on_gif_frame_loaded)

            # 绑定到 Label
            self.imageLabel.setMovie(self.movie)
            # 启动播放
            self.movie.start()
        else:
            # 静态图片逻辑
            self.isGif = False
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                print(f"错误：无法加载图片 {image_path}")
                return
            self.imageLabel.setPixmap(pixmap)
            # 静态图直接设置尺寸
            self.imageLabel.setFixedSize(pixmap.size())
            # 同步设置窗口尺寸
            self.setFixedSize(pixmap.size())

    def _on_gif_frame_loaded(self):
        """GIF 帧加载完成后设置有效尺寸"""
        if not self.movie:
            return
        # 获取 GIF 有效尺寸（避免 -1,-1）
        gif_size = self.movie.scaledSize()
        if gif_size.width() > 0 and gif_size.height() > 0:
            # 设置 Label 尺寸
            self.imageLabel.setFixedSize(gif_size)
            # 同步设置窗口尺寸（关键：让窗口显示）
            self.setFixedSize(gif_size)
            # 只执行一次，避免重复触发
            self.movie.frameChanged.disconnect(self._on_gif_frame_loaded)

    def hideToTray(self):
        self.setVisible(False)
        # 仅 GIF 时暂停播放
        if self.isGif and self.movie and self.movie.state() == QMovie.Running:
            self.movie.setPaused(True)

    def showFromTray(self):
        self.setVisible(True)
        self.raise_()
        self.activateWindow()
        # 仅 GIF 时恢复播放
        if self.isGif and self.movie and self.movie.state() == QMovie.Paused:
            self.movie.setPaused(False)

    def emojiDownload(self):
        if self._emojiSelecter:
            return

        self._emojiSelecter = emoji_selecter.emoSearchListWidget()
        self._emojiSelecter.show()

        def _setEmoToNone():
            self._emojiSelecter = None

        self._emojiSelecter.readyToDestory.connect(_setEmoToNone)

    def vdoDownload(self):
        if self._videoDownloadWidget:
            return

        self._videoDownloadWidget = video_download_widget.vdoDownWidget()
        self._videoDownloadWidget.show()

        def _setVdoToNone():
            self._videoDownloadWidget = None
        
        self._videoDownloadWidget.readyToDestory.connect(_setVdoToNone)

    def onDmPlayer(self, checked):
        if not self._bulletscreenPlayer:
            self._bulletscreenPlayer = bulletscreen_player.bulletscreenObject(self)

        if checked:
            if self._bulletscreenPlayer.isRunning():
                return

            if not self._blivedmWidget:
                self._blivedmWidget = blivedm_widget.blivedmObject(self)

            self._blivedmWidget.runBlivedm()
            self._bulletscreenPlayer.runPlayer()
        else:
            if not self._bulletscreenPlayer.isRunning():
                return

            self._bulletscreenPlayer.stopPlayer()

            if self._bulletscreenWidget:
                return

            self._blivedmWidget.stopBlivedm()

    def onDmWidget(self, checked):
        if checked:
            pass
        else:
            pass

    def openSettingPage(self):
        if self._settingPageWidget:
            return

        self._settingPageWidget = setting_page_vibe_c.settingPage()
        self._settingPageWidget.show()

        def _setSetPageToNone():
            self._settingPageWidget = None

        self._settingPageWidget.readyToDestory.connect(_setSetPageToNone)

    # 窗口隐藏事件（兜底：比如用户手动隐藏窗口也暂停GIF）
    def hideEvent(self, event):
        super().hideEvent(event)
        if self.isGif and self.movie and self.movie.state() == QMovie.Running:
            self.movie.setPaused(True)

    # 窗口显示事件（兜底：显示时恢复GIF）
    def showEvent(self, event):
        super().showEvent(event)
        if self.isGif and self.movie and self.movie.state() == QMovie.Paused:
            self.movie.setPaused(False)

    # 拖拽逻辑（保留）
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._offsetPos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton and not self._offsetPos.isNull():
            self.move(event.globalPosition().toPoint() - self._offsetPos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.RightButton:
            self._rightMenu.exec(QCursor.pos())
