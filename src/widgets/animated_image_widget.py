from pathlib import Path
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QMenu
from PySide6.QtGui import QPixmap, QMouseEvent, QCursor, QAction, QMovie
from PySide6.QtCore import Qt, QPoint


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
        # 初始设置最小尺寸，避免负尺寸报错
        # self.image_label.setMinimumSize(QSize(1, 1))

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

    def _initRightMenu(self):
        self._rightMenu = QMenu(self)
        self._rightMenu.setObjectName("WidgetMenu")

        self._rightMenu.setStyleSheet("""
            QMenu#WidgetMenu {
                padding: 4px 2px;  /* 菜单上下内边距缩小 */
                border-radius: 6px;  /* 轻量圆角，不增加过多渲染开销 */
            }
            QMenu#WidgetMenu::item {
                padding: 5px 20px;  /* 菜单项内边距缩小 */
                margin: 0 2px;      /* 菜单项外边距缩小 */
                border-radius: 6px; /* 新增：菜单项圆角（值可根据需求调整） */
            }
            QMenu#WidgetMenu::item:selected {
                background-color: palette(highlight);  /* 系统原生高亮背景 */
                color: palette(highlightedText);       /* 系统原生高亮文字色 */
                border-radius: 6px; /* 新增：选中态也保留圆角，视觉统一 */
            }
        """)

        self.hide_to_tray_action = QAction("隐藏界面", self)
        self.hide_to_tray_action.triggered.connect(self.hideToTray)
        self._rightMenu.addAction(self.hide_to_tray_action)

        self._rightMenu.addSeparator()

        self.quitAppAction = QAction("退出应用", self)
        self.quitAppAction.triggered.connect(lambda: QApplication.quit())
        self._rightMenu.addAction(self.quitAppAction)

    # ========== 修改2：优化load_image函数，支持动态切换图片/GIF ==========
    def _loadAnimatedImage(self, image_path: str) -> bool:
        """加载/切换图片/GIF（优化后支持动态切换，避免控件异常）"""
        if not Path(image_path).exists():
            print(f"错误：图片路径 {image_path} 不存在")
            self.isGif = False
            return False

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
            # 设置无限循环（-1 = 无限循环）
            self.movie.loopCount = -1

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
                return False
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
        """隐藏到托盘（自动暂停GIF，优化性能）"""
        self.setVisible(False)
        # 仅 GIF 时暂停播放
        if self.isGif and self.movie and self.movie.state() == QMovie.Running:
            self.movie.setPaused(True)

    def showFromTray(self):
        """从托盘显示（自动恢复GIF播放）"""
        self.setVisible(True)
        self.raise_()
        self.activateWindow()
        # 仅 GIF 时恢复播放
        if self.isGif and self.movie and self.movie.state() == QMovie.Paused:
            self.movie.setPaused(False)

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
