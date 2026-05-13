"""
Accounts Page - Trang quản lý tài khoản với bảng, tìm kiếm, filter
"""

import webbrowser
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QHeaderView,
    QTableWidgetItem,
    QAbstractItemView,
)

from qfluentwidgets import (
    ScrollArea,
    TitleLabel,
    CaptionLabel,
    SearchLineEdit,
    ComboBox,
    TableWidget,
    PushButton,
    FluentIcon,
    InfoBar,
    InfoBarPosition,
    MessageBox,
    BodyLabel,
    CardWidget,
)

from src.storage import AccountStorage
from src.models import Account


class AccountsPage(QWidget):
    """Trang quản lý tài khoản"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("accountsPage")

        self.storage = AccountStorage()
        self.accounts: list[Account] = []
        self.filtered_accounts: list[Account] = []

        self._init_ui()
        self._load_data()

    def _init_ui(self):
        """Khởi tạo giao diện"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 28)
        layout.setSpacing(16)

        # Header
        self._init_header(layout)

        # Filter bar
        self._init_filters(layout)

        # Info bar
        self._init_info_bar(layout)

        # Table
        self._init_table(layout)

    def _init_header(self, parent_layout):
        """Header với title và actions"""
        header = QHBoxLayout()
        header.setSpacing(12)

        # Title
        title_layout = QVBoxLayout()
        title_layout.setSpacing(4)
        title = TitleLabel("🎮 Quản lý tài khoản")
        title_layout.addWidget(title)
        subtitle = CaptionLabel("Tìm kiếm, lọc và quản lý tất cả tài khoản đã crawl")
        subtitle.setStyleSheet("color: #888; font-size: 13px;")
        title_layout.addWidget(subtitle)
        header.addLayout(title_layout)

        header.addStretch()

        # Actions
        self.refresh_btn = PushButton(FluentIcon.SYNC, "Làm mới")
        self.refresh_btn.clicked.connect(self._load_data)
        header.addWidget(self.refresh_btn)

        self.delete_btn = PushButton(FluentIcon.DELETE, "Xóa tất cả")
        self.delete_btn.setStyleSheet("PushButton { color: #EF5350; }")
        self.delete_btn.clicked.connect(self._confirm_delete_all)
        header.addWidget(self.delete_btn)

        parent_layout.addLayout(header)

    def _init_filters(self, parent_layout):
        """Filter bar"""
        filter_card = CardWidget(self)
        filter_layout = QHBoxLayout(filter_card)
        filter_layout.setContentsMargins(16, 12, 16, 12)
        filter_layout.setSpacing(12)

        # Search
        self.search_input = SearchLineEdit(self)
        self.search_input.setPlaceholderText("Tìm kiếm theo ID Game, Rank...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.search_input)

        # Shop filter
        self.shop_filter = ComboBox(self)
        self.shop_filter.setFixedWidth(180)
        self.shop_filter.addItem("Tất cả Shop")
        self.shop_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.shop_filter)

        # Rank filter
        self.rank_filter = ComboBox(self)
        self.rank_filter.setFixedWidth(160)
        self.rank_filter.addItem("Tất cả Rank")
        self.rank_filter.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.rank_filter)

        # Sort
        self.sort_combo = ComboBox(self)
        self.sort_combo.setFixedWidth(180)
        self.sort_combo.addItems([
            "Mặc định",
            "Giá: Thấp → Cao",
            "Giá: Cao → Thấp",
            "Tướng: Nhiều → Ít",
            "Skin: Nhiều → Ít",
        ])
        self.sort_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.sort_combo)

        filter_layout.addStretch()

        parent_layout.addWidget(filter_card)

    def _init_info_bar(self, parent_layout):
        """Info bar hiển thị số lượng kết quả"""
        self.info_label = CaptionLabel("", self)
        self.info_label.setStyleSheet("color: #0078D4; font-size: 12px; padding: 4px 0;")
        parent_layout.addWidget(self.info_label)

    def _init_table(self, parent_layout):
        """Bảng dữ liệu"""
        self.table = TableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "STT", "ID Game", "Rank", "Tướng", "Skin", "Giá", "Shop"
        ])

        # Table settings
        self.table.setSelectRightClickedRow(True)
        self.table.setBorderVisible(True)
        self.table.setBorderRadius(8)
        self.table.setWordWrap(False)

        # Column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        header.setSectionResizeMode(6, QHeaderView.Fixed)

        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 80)
        self.table.setColumnWidth(5, 120)
        self.table.setColumnWidth(6, 140)

        # Selection
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Double click to open link
        self.table.doubleClicked.connect(self._on_row_double_click)

        parent_layout.addWidget(self.table)

    def _load_data(self):
        """Load dữ liệu từ storage"""
        self.accounts = self.storage.load()
        self._update_filter_options()
        self._apply_filters()

    def _update_filter_options(self):
        """Cập nhật options cho filter dropdowns"""
        # Shop filter
        shops = sorted(set(acc.shop for acc in self.accounts if acc.shop))
        self.shop_filter.blockSignals(True)
        current_shop = self.shop_filter.currentText()
        self.shop_filter.clear()
        self.shop_filter.addItem("Tất cả Shop")
        for shop in shops:
            self.shop_filter.addItem(shop)
        # Restore selection
        idx = self.shop_filter.findText(current_shop)
        if idx >= 0:
            self.shop_filter.setCurrentIndex(idx)
        self.shop_filter.blockSignals(False)

        # Rank filter
        ranks = sorted(set(acc.rank for acc in self.accounts if acc.rank))
        self.rank_filter.blockSignals(True)
        current_rank = self.rank_filter.currentText()
        self.rank_filter.clear()
        self.rank_filter.addItem("Tất cả Rank")
        for rank in ranks:
            self.rank_filter.addItem(rank)
        idx = self.rank_filter.findText(current_rank)
        if idx >= 0:
            self.rank_filter.setCurrentIndex(idx)
        self.rank_filter.blockSignals(False)

    def _on_filter_changed(self):
        """Khi filter thay đổi"""
        self._apply_filters()

    def _apply_filters(self):
        """Áp dụng tất cả filters và hiển thị kết quả"""
        filtered = list(self.accounts)

        # Search filter
        search_text = self.search_input.text().strip().lower()
        if search_text:
            filtered = [
                acc for acc in filtered
                if search_text in acc.id_game.lower()
                or search_text in acc.rank.lower()
                or search_text in acc.shop.lower()
                or search_text in acc.gia.lower()
            ]

        # Shop filter
        shop_text = self.shop_filter.currentText()
        if shop_text and shop_text != "Tất cả Shop":
            filtered = [acc for acc in filtered if acc.shop == shop_text]

        # Rank filter
        rank_text = self.rank_filter.currentText()
        if rank_text and rank_text != "Tất cả Rank":
            filtered = [acc for acc in filtered if acc.rank == rank_text]

        # Sort
        sort_text = self.sort_combo.currentText()
        if sort_text == "Giá: Thấp → Cao":
            filtered.sort(key=lambda x: x.price_numeric)
        elif sort_text == "Giá: Cao → Thấp":
            filtered.sort(key=lambda x: x.price_numeric, reverse=True)
        elif sort_text == "Tướng: Nhiều → Ít":
            filtered.sort(key=lambda x: x.champions_count, reverse=True)
        elif sort_text == "Skin: Nhiều → Ít":
            filtered.sort(key=lambda x: x.skins_count, reverse=True)

        self.filtered_accounts = filtered
        self._render_table()

    def _render_table(self):
        """Render dữ liệu vào bảng"""
        self.table.setRowCount(0)
        self.table.setRowCount(len(self.filtered_accounts))

        for row, acc in enumerate(self.filtered_accounts):
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(acc.id_game))
            self.table.setItem(row, 2, QTableWidgetItem(acc.rank))
            self.table.setItem(row, 3, QTableWidgetItem(acc.so_tuong))
            self.table.setItem(row, 4, QTableWidgetItem(acc.so_skin))
            self.table.setItem(row, 5, QTableWidgetItem(acc.gia))
            self.table.setItem(row, 6, QTableWidgetItem(acc.shop))

        # Update info
        total = len(self.accounts)
        showing = len(self.filtered_accounts)
        if showing == total:
            self.info_label.setText(f"Hiển thị tất cả {total} tài khoản")
        else:
            self.info_label.setText(f"Hiển thị {showing}/{total} tài khoản (đã lọc)")

    def _on_row_double_click(self, index):
        """Mở link khi double click"""
        row = index.row()
        if 0 <= row < len(self.filtered_accounts):
            acc = self.filtered_accounts[row]
            if acc.link:
                webbrowser.open(acc.link)

    def _confirm_delete_all(self):
        """Xác nhận xóa tất cả"""
        if not self.accounts:
            return

        msg = MessageBox(
            "Xác nhận xóa",
            f"Bạn có chắc muốn xóa tất cả {len(self.accounts)} tài khoản?\n"
            "Hành động này không thể hoàn tác.",
            self,
        )
        if msg.exec():
            self.storage.clear()
            self._load_data()
