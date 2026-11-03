"""读「降低游戏画质」留下的全局原始档位快照。

快照文件是 config/graphics_low_snapshot.yml，不带实例目录。
这里不 import 降画质插件的模块，因为两个插件是各自独立的包、
分开安装，跨插件 import 会在只装恢复画质时直接崩掉。
直接按同一个 YamlConfig 模块名打开同一个文件即可。

文件不存在（没装降画质插件、或从没跑过）时读到的都是空串，
调用方据此回落到兜底档位。
"""

from __future__ import annotations

from one_dragon.base.config.yaml_config import YamlConfig

# 与 graphics_low_snapshot.MODULE_NAME 必须一致
MODULE_NAME = 'graphics_low_snapshot'


class LowSnapshotReader(YamlConfig):
    """只读地打开降画质的快照文件。"""

    def __init__(self) -> None:
        YamlConfig.__init__(self, MODULE_NAME)

    @property
    def original_fps(self) -> str:
        """原始帧率，空串表示没有记录。"""
        return self.get('original_fps', '')

    @property
    def original_render_scale(self) -> str:
        """原始渲染精度，空串表示没有记录。"""
        return self.get('original_render_scale', '')

    @property
    def original_antialias(self) -> str:
        """原始抗锯齿，空串表示没有记录。"""
        return self.get('original_antialias', '')

    @property
    def original_font(self) -> str:
        """原始字体选项，空串表示没有记录。

        降画质插件切到「其他」页之后才补记这一项，所以老版本留下的快照里可能没有它，
        那时即使 has_snapshot 为 True，original_font 也还是空串。
        """
        return self.get('original_font', '')

    @property
    def snapshot_date(self) -> str:
        """记录日期，空串表示没有记录。"""
        return self.get('snapshot_date', '')

    @property
    def has_snapshot(self) -> bool:
        """是否有可用的原始档位记录。"""
        return self.original_fps != ''
