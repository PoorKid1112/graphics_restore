"""恢复画质插件的设置页。

这里只放「兜底档位」：正常情况下恢复成「降低游戏画质」记下的原始档位，
只有那份记录缺失（没装降画质插件、或从没跑成功过）时才用这里的值。
页面下方会显示当前读到的原始档位，方便对照。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout, QWidget
from qfluentwidgets import CaptionLabel, FluentIcon

from one_dragon.base.config.config_item import ConfigItem
from one_dragon.utils.log_utils import log
from one_dragon_qt.services.app_setting.app_setting_provider import GroupIdMixin
from one_dragon_qt.utils.config_utils import get_prop_adapter
from one_dragon_qt.widgets.setting_card.combo_box_setting_card import (
    ComboBoxSettingCard,
)
from one_dragon_qt.widgets.vertical_scroll_interface import VerticalScrollInterface

from . import graphics_restore_const
from .graphics_restore_config import GraphicsRestoreConfig
from .graphics_restore_snapshot import LowSnapshotReader

if TYPE_CHECKING:
    from one_dragon.base.operation.one_dragon_context import OneDragonContext


# 下拉选项必须和游戏内文字一一对应
FPS_OPTIONS: list[ConfigItem] = [
    ConfigItem('30 帧', '30'),
    ConfigItem('60 帧', '60'),
    ConfigItem('无限制', '无限制'),
]
RENDER_SCALE_OPTIONS: list[ConfigItem] = [
    ConfigItem('0.8', '0.8'),
    ConfigItem('1.0', '1.0'),
    ConfigItem('1.2', '1.2'),
]
ANTIALIAS_OPTIONS: list[ConfigItem] = [
    ConfigItem('关闭', '关闭'),
    ConfigItem('TAA', 'TAA'),
    ConfigItem('SMAA', 'SMAA'),
]


class GraphicsRestoreSettingInterface(VerticalScrollInterface, GroupIdMixin):
    """恢复画质的独立设置页。"""

    def __init__(self, ctx: OneDragonContext, parent: QWidget | None = None) -> None:
        super().__init__(
            content_widget=None,
            object_name='graphics_restore_setting_interface',
            nav_text_cn='恢复游戏画质',
            parent=parent,
        )
        self.ctx: OneDragonContext = ctx
        self.config: GraphicsRestoreConfig | None = None
        self.fps_opt: ComboBoxSettingCard | None = None
        self.render_scale_opt: ComboBoxSettingCard | None = None
        self.antialias_opt: ComboBoxSettingCard | None = None
        self.snapshot_label: CaptionLabel | None = None

    def get_content_widget(self) -> QWidget:
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        intro = CaptionLabel(
            '正常情况下恢复成「降低游戏画质」第一次运行时记下的档位，'
            '只有那份记录缺失时才用下面这三个兜底值。',
            widget,
        )
        intro.setWordWrap(True)
        layout.addWidget(intro)

        self.fps_opt = ComboBoxSettingCard(
            icon=FluentIcon.SPEED_HIGH,
            title='兜底帧率',
            content='没有原始记录时恢复成这一档',
            options_list=FPS_OPTIONS,
        )
        layout.addWidget(self.fps_opt)

        self.render_scale_opt = ComboBoxSettingCard(
            icon=FluentIcon.ZOOM,
            title='兜底渲染精度',
            content='没有原始记录时恢复成这一档',
            options_list=RENDER_SCALE_OPTIONS,
        )
        layout.addWidget(self.render_scale_opt)

        self.antialias_opt = ComboBoxSettingCard(
            icon=FluentIcon.BRUSH,
            title='兜底抗锯齿',
            content='没有原始记录时恢复成这一档',
            options_list=ANTIALIAS_OPTIONS,
        )
        layout.addWidget(self.antialias_opt)

        self.snapshot_label = CaptionLabel('正在读取原始档位记录…', widget)
        self.snapshot_label.setWordWrap(True)
        layout.addWidget(self.snapshot_label)

        layout.addStretch(1)
        return widget

    def on_interface_shown(self) -> None:
        super().on_interface_shown()

        self.config = self.ctx.run_context.get_config(
            app_id=graphics_restore_const.APP_ID,
            instance_idx=self.ctx.current_instance_idx,
            group_id=self.group_id,
        )
        self.fps_opt.init_with_adapter(get_prop_adapter(self.config, 'fallback_fps'))
        self.render_scale_opt.init_with_adapter(
            get_prop_adapter(self.config, 'fallback_render_scale')
        )
        self.antialias_opt.init_with_adapter(
            get_prop_adapter(self.config, 'fallback_antialias')
        )
        self._update_snapshot_display()

    def _update_snapshot_display(self) -> None:
        """显示「降低游戏画质」记下的原始档位。"""
        if self.snapshot_label is None or self.config is None:
            return

        try:
            snapshot = LowSnapshotReader()
        except Exception:
            log.warning('读不到「降低游戏画质」的快照', exc_info=True)
            self.snapshot_label.setText('没有装「降低游戏画质」，会直接使用上面的兜底档位')
            return

        if not snapshot.has_snapshot:
            self.snapshot_label.setText('「降低游戏画质」还没记录原始档位，会直接使用上面的兜底档位')
            return

        self.snapshot_label.setText(
            f'当前原始档位：帧率 {snapshot.original_fps} / 渲染精度 '
            f'{snapshot.original_render_scale} / 抗锯齿 {snapshot.original_antialias}'
            f'（{snapshot.snapshot_date} 记录，可在「降低游戏画质」的设置页里清空）'
        )
