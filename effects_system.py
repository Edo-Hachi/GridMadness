import pyxel
import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

@dataclass
class Particle:
    """パーティクルの基本データクラス"""
    x: float
    y: float
    vx: float  # X方向速度
    vy: float  # Y方向速度
    life: float  # 残り寿命（0-1）
    max_life: float  # 最大寿命
    color: int
    size: float
    gravity: float = 0.1
    bounce: float = 0.3
    fade_speed: float = 0.02

@dataclass
class ManaParticle(Particle):
    """マナパーティクル（クリスタルクリック時）"""
    sparkle_timer: float = 0.0
    sparkle_phase: float = 0.0
    trail_positions: List[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.trail_positions is None:
            self.trail_positions = []

@dataclass
class PachinkoParticle(Particle):
    """パチンコエフェクト用パーティクル"""
    angle: float = 0.0
    rotation_speed: float = 0.0
    scale: float = 1.0
    pulse_timer: float = 0.0

class EffectsSystem:
    """視覚エフェクトシステム - パチンコ心理学を応用した脳汁システム！"""
    
    def __init__(self):
        self.mana_particles: List[ManaParticle] = []
        self.pachinko_particles: List[PachinkoParticle] = []
        self.bonus_time_active = False
        self.bonus_time_timer = 0.0
        self.bonus_time_duration = 300  # 5秒（60fps想定）
        self.screen_shake_intensity = 0.0
        self.screen_shake_timer = 0.0
        self.combo_multiplier = 1.0
        self.combo_timer = 0.0
        
        # エフェクト強度設定
        self.mana_intensity = 1.0
        self.pachinko_intensity = 1.0
        
        # パフォーマンス最適化設定
        self.max_mana_particles = 150  # マナパーティクルの最大数
        self.max_pachinko_particles = 100  # パチンコパーティクルの最大数
        self.max_background_mana = 30  # 背景マナの最大数
        self.performance_mode = False  # パフォーマンスモード（軽量化）
        self.particle_cull_distance = 300  # 画面外パーティクルの削除距離
        
        # 背景マナの雨エフェクト
        self.background_mana: List[ManaParticle] = []
        self.mana_rain_timer = 0
        
        # パチンコ心理学的要素
        self.near_miss_chance = 0.15  # ニアミス発生確率（15%）
        self.expectation_buildup = 0.0  # 期待感の蓄積値
        self.consecutive_clicks = 0  # 連続クリック数
        self.last_big_win_timer = 0  # 最後の大当たりからの時間
        self.tease_effects_active = False  # 焦らしエフェクト中
        self.tease_timer = 0
        
        # 段階的報酬システム
        self.reward_stages = [
            {"threshold": 5, "multiplier": 1.2, "message": "いい感じ！"},
            {"threshold": 10, "multiplier": 1.5, "message": "調子に乗ってきた！"},
            {"threshold": 20, "multiplier": 2.0, "message": "大当たりの予感...!"},
            {"threshold": 30, "multiplier": 3.0, "message": "超大当たり！！！"}
        ]
        self.current_stage = 0
        
        # 遅延実行システム（pyxel.run_laterの代替）
        self.delayed_effects = []  # [(timer, callback), ...]
        
        # ステージメッセージ表示用
        self.stage_message = ""
        self.stage_message_timer = 0
        
    def create_mana_explosion(self, x: float, y: float, intensity: float = 1.0):
        """マナ爆発エフェクトを生成（クリスタルクリック時）- 脳汁ドバドバ！"""
        # パフォーマンスモードではパーティクル数を減らす
        base_count = 20 if not self.performance_mode else 10
        particle_count = int(base_count * intensity * self.mana_intensity)
        
        # パーティクル数制限をチェック
        current_count = len(self.mana_particles)
        if current_count + particle_count > self.max_mana_particles:
            particle_count = max(0, self.max_mana_particles - current_count)
        
        for _ in range(particle_count):
            # ランダムな方向と速度
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 10) * intensity
            
            # マナの色（青系、緑系、紫系、金色をランダム）
            mana_colors = [1, 3, 5, 6, 11, 12, 13, 10]  # 青、緑、紫、金系
            color = random.choice(mana_colors)
            
            particle = ManaParticle(
                x=x + random.uniform(-8, 8),
                y=y + random.uniform(-8, 8),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - random.uniform(2, 5),  # 上向きバイアス
                life=1.0,
                max_life=random.uniform(80, 150),  # 1.3-2.5秒
                color=color,
                size=random.uniform(1.5, 4),
                gravity=random.uniform(0.08, 0.2),
                bounce=random.uniform(0.3, 0.7),
                fade_speed=random.uniform(0.006, 0.015),
                sparkle_timer=random.uniform(0, 30),
                sparkle_phase=random.uniform(0, 2 * math.pi)
            )
            
            self.mana_particles.append(particle)
            
        # 画面振動を追加（気持ちよさアップ）
        self.add_screen_shake(1.5, 8)
        
        # 心理学的要素を更新
        self.update_psychology_system()
    
    def create_pachinko_burst(self, x: float, y: float):
        """パチンコ風バーストエフェクト（ボーナスタイム用）- 射的心を煽る！"""
        # パフォーマンスモードではパーティクル数を減らす
        base_count = 35 if not self.performance_mode else 15
        particle_count = int(base_count * self.pachinko_intensity)
        
        # パーティクル数制限をチェック
        current_count = len(self.pachinko_particles)
        if current_count + particle_count > self.max_pachinko_particles:
            particle_count = max(0, self.max_pachinko_particles - current_count)
        
        for _ in range(particle_count):
            # 放射状に広がる
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(4, 15)
            
            # 派手な色（赤、黄、オレンジ、白、ピンク）
            pachinko_colors = [8, 9, 10, 7, 14, 15, 4]
            color = random.choice(pachinko_colors)
            
            particle = PachinkoParticle(
                x=x + random.uniform(-3, 3),
                y=y + random.uniform(-3, 3),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                life=1.0,
                max_life=random.uniform(120, 200),  # 2-3.3秒
                color=color,
                size=random.uniform(2, 5),
                gravity=random.uniform(0.03, 0.1),
                bounce=random.uniform(0.5, 0.9),
                fade_speed=random.uniform(0.003, 0.01),
                angle=random.uniform(0, 2 * math.pi),
                rotation_speed=random.uniform(-0.4, 0.4),
                scale=random.uniform(0.8, 2.0),
                pulse_timer=random.uniform(0, 60)
            )
            
            self.pachinko_particles.append(particle)
    
    def start_bonus_time(self, duration: float = 300):
        """ボーナスタイムを開始 - パチンコ台のような興奮！"""
        self.bonus_time_active = True
        self.bonus_time_timer = duration
        self.combo_multiplier = 2.0
        self.screen_shake_intensity = 3.0
        self.screen_shake_timer = 45
        
        # 画面全体にパチンコエフェクト（連鎖爆発）
        for i in range(8):
            x = random.uniform(30, 226)
            y = random.uniform(30, 226)
            # 時間差で爆発させる（遅延実行システム使用）
            delay_timer = i * 5
            self.delayed_effects.append((delay_timer, lambda px=x, py=y: self.create_pachinko_burst(px, py)))
    
    def create_background_mana_rain(self):
        """背景にマナの雨を降らせる"""
        if self.mana_rain_timer <= 0 and len(self.background_mana) < self.max_background_mana:
            # パフォーマンスモードでは生成数を減らす
            max_spawn = 3 if not self.performance_mode else 1
            spawn_count = random.randint(1, max_spawn)
            
            # 新しいマナ粒子を画面上部に生成
            for _ in range(min(spawn_count, self.max_background_mana - len(self.background_mana))):
                particle = ManaParticle(
                    x=random.uniform(-10, 266),
                    y=random.uniform(-20, -5),
                    vx=random.uniform(-0.5, 0.5),
                    vy=random.uniform(0.5, 2.0),
                    life=1.0,
                    max_life=random.uniform(200, 400),  # 長寿命
                    color=random.choice([1, 3, 5, 6, 11]),  # 落ち着いた色
                    size=random.uniform(0.5, 1.5),
                    gravity=random.uniform(0.01, 0.03),
                    bounce=0.1,
                    fade_speed=random.uniform(0.002, 0.005),
                    sparkle_timer=random.uniform(0, 60),
                    sparkle_phase=random.uniform(0, 2 * math.pi)
                )
                self.background_mana.append(particle)
            
            self.mana_rain_timer = random.randint(15, 45)  # 次の雨まで
        else:
            self.mana_rain_timer -= 1
    
    def update_psychology_system(self):
        """パチンコ心理学システムの更新 - 脳内麻薬放出装置！"""
        self.consecutive_clicks += 1
        self.last_big_win_timer += 1
        
        # 期待感を少しずつ蓄積（ドーパミンの準備）
        self.expectation_buildup = min(1.0, self.expectation_buildup + 0.05)
        
        # 段階的報酬システムのチェック
        self.check_reward_stages()
        
        # ニアミス演出の判定（「惜しかった！」を演出）
        if random.random() < self.near_miss_chance:
            self.trigger_near_miss_effect()
    
    def trigger_near_miss_effect(self):
        """ニアミス演出 - 「あと少しで大当たりだったのに！」"""
        self.tease_effects_active = True
        self.tease_timer = 120  # 2秒間の焦らし
        
        # 期待感を大幅アップ（ここがミソ！）
        self.expectation_buildup = min(1.0, self.expectation_buildup + 0.3)
        
        # 特別なエフェクトで「惜しさ」を演出
        self.create_tease_effect()
    
    def create_tease_effect(self):
        """焦らしエフェクト - 「もう少しで...」の演出"""
        # 画面全体に金色のキラキラを散らす
        for _ in range(30):
            x = random.uniform(0, 256)
            y = random.uniform(0, 256)
            
            particle = ManaParticle(
                x=x, y=y,
                vx=random.uniform(-2, 2),
                vy=random.uniform(-2, 2),
                life=1.0,
                max_life=random.uniform(60, 90),
                color=10,  # 金色
                size=random.uniform(2, 4),
                gravity=0.02,
                bounce=0.8,
                fade_speed=0.01,
                sparkle_timer=0,
                sparkle_phase=random.uniform(0, 2 * math.pi)
            )
            self.mana_particles.append(particle)
        
        # 特別な音と振動で期待感を高める
        self.add_screen_shake(0.8, 60)  # 長めの小さな振動
    
    def check_reward_stages(self):
        """段階的報酬システム - 小さな成功でも達成感を与える"""
        for i, stage in enumerate(self.reward_stages):
            if (self.consecutive_clicks >= stage["threshold"] and 
                self.current_stage <= i):
                self.current_stage = i + 1
                self.trigger_stage_reward(stage)
                break
    
    def trigger_stage_reward(self, stage):
        """段階報酬の発動 - 「やった！進歩してる！」"""
        # エフェクト強度をアップ
        self.mana_intensity *= stage["multiplier"]
        
        # 特別なお祝いエフェクト
        for _ in range(int(15 * stage["multiplier"])):
            x = random.uniform(50, 206)
            y = random.uniform(50, 206)
            self.create_mana_explosion(x, y, stage["multiplier"])
        
        # メッセージ表示用のフラグを設定
        self.stage_message = stage["message"]
        self.stage_message_timer = 180  # 3秒間表示
    
    def trigger_big_win(self):
        """大当たり演出 - 最大の脳汁放出！"""
        self.last_big_win_timer = 0
        self.consecutive_clicks = 0
        self.expectation_buildup = 0.0
        self.current_stage = 0
        
        # ボーナスタイム開始
        self.start_bonus_time(450)  # 7.5秒のロングボーナス
        
        # 大爆発エフェクト
        for _ in range(50):
            x = random.uniform(30, 226)
            y = random.uniform(30, 226)
            self.create_mana_explosion(x, y, 3.0)
            self.create_pachinko_burst(x, y)
        
        # 最大振動
        self.add_screen_shake(5.0, 90)
    
    def should_trigger_big_win(self) -> bool:
        """大当たりを発動すべきか判定 - 絶妙なタイミングで！"""
        # 基本確率は低いが、条件で上がる
        base_chance = 0.02  # 2%
        
        # 期待感が高いほど確率アップ
        expectation_bonus = self.expectation_buildup * 0.05
        
        # 長時間大当たりがないと確率アップ（救済システム）
        drought_bonus = min(0.1, self.last_big_win_timer * 0.0001)
        
        total_chance = base_chance + expectation_bonus + drought_bonus
        
        return random.random() < total_chance
    
    def add_screen_shake(self, intensity: float, duration: float = 15):
        """画面振動エフェクトを追加"""
        self.screen_shake_intensity = max(self.screen_shake_intensity, intensity)
        self.screen_shake_timer = max(self.screen_shake_timer, duration)
    
    def get_screen_shake_offset(self) -> Tuple[float, float]:
        """画面振動のオフセットを取得"""
        if self.screen_shake_timer <= 0:
            return 0.0, 0.0
        
        shake_x = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
        shake_y = random.uniform(-self.screen_shake_intensity, self.screen_shake_intensity)
        return shake_x, shake_y
    
    def update(self):
        """エフェクトシステムの更新"""
        # 背景マナの雨を生成
        self.create_background_mana_rain()
        
        # マナパーティクルの更新
        self.mana_particles = [p for p in self.mana_particles if self._update_mana_particle(p)]
        self.background_mana = [p for p in self.background_mana if self._update_mana_particle(p)]
        
        # パチンコパーティクルの更新
        self.pachinko_particles = [p for p in self.pachinko_particles if self._update_pachinko_particle(p)]
        
        # ボーナスタイムの管理
        if self.bonus_time_active:
            self.bonus_time_timer -= 1
            if self.bonus_time_timer <= 0:
                self.bonus_time_active = False
                self.combo_multiplier = 1.0
                
            # ボーナスタイム中は追加エフェクト
            if random.randint(1, 10) == 1:  # 10%の確率
                x = random.uniform(50, 206)
                y = random.uniform(50, 206)
                self.create_pachinko_burst(x, y)
        
        # コンボタイマーの減少
        if self.combo_timer > 0:
            self.combo_timer -= 1
        
        # 画面振動の減衰
        if self.screen_shake_timer > 0:
            self.screen_shake_timer -= 1
            self.screen_shake_intensity *= 0.92
        
        # 遅延実行システムの処理
        remaining_effects = []
        for timer, callback in self.delayed_effects:
            if timer <= 0:
                # タイマーが0になったので実行
                callback()
            else:
                # まだ時間があるので継続
                remaining_effects.append((timer - 1, callback))
        self.delayed_effects = remaining_effects
        
        # ステージメッセージタイマーの減少
        if self.stage_message_timer > 0:
            self.stage_message_timer -= 1
        
        # 焦らしエフェクトタイマーの減少
        if self.tease_timer > 0:
            self.tease_timer -= 1
            if self.tease_timer <= 0:
                self.tease_effects_active = False
    
    def _update_mana_particle(self, particle: ManaParticle) -> bool:
        """マナパーティクルの個別更新"""
        # 位置更新
        particle.x += particle.vx
        particle.y += particle.vy
        
        # 重力適用
        particle.vy += particle.gravity
        
        # 画面端での跳ね返り
        if particle.x <= 0 or particle.x >= 256:
            particle.vx *= -particle.bounce
            particle.x = max(0, min(256, particle.x))
        
        if particle.y >= 256:
            particle.vy *= -particle.bounce
            particle.y = 256
            particle.vx *= 0.8  # 地面摩擦
        
        # キラキラエフェクト更新
        particle.sparkle_timer += 1
        particle.sparkle_phase += 0.2
        
        # 軌跡更新
        particle.trail_positions.append((particle.x, particle.y))
        if len(particle.trail_positions) > 5:
            particle.trail_positions.pop(0)
        
        # 寿命管理
        particle.life -= particle.fade_speed
        
        return particle.life > 0 and particle.y > -50
    
    def _update_pachinko_particle(self, particle: PachinkoParticle) -> bool:
        """パチンコパーティクルの個別更新"""
        # 位置更新
        particle.x += particle.vx
        particle.y += particle.vy
        
        # 重力適用
        particle.vy += particle.gravity
        
        # 回転更新
        particle.angle += particle.rotation_speed
        particle.pulse_timer += 1
        
        # 画面端での跳ね返り（より派手に）
        if particle.x <= 0 or particle.x >= 256:
            particle.vx *= -particle.bounce
            particle.x = max(0, min(256, particle.x))
            # 跳ね返り時にスパーク
            if random.randint(1, 3) == 1:
                self.create_mana_explosion(particle.x, particle.y, 0.3)
        
        if particle.y >= 256:
            particle.vy *= -particle.bounce
            particle.y = 256
            particle.vx *= 0.7
            # 地面衝突時にスパーク
            if random.randint(1, 2) == 1:
                self.create_mana_explosion(particle.x, particle.y, 0.4)
        
        # 寿命管理
        particle.life -= particle.fade_speed
        
        return particle.life > 0 and particle.y > -50
    
    def draw(self):
        """エフェクトの描画"""
        # 背景マナの雨を描画（最背面）
        for particle in self.background_mana:
            self._draw_mana_particle(particle, alpha_multiplier=0.6)
        
        # マナパーティクルを描画
        for particle in self.mana_particles:
            self._draw_mana_particle(particle)
        
        # パチンコパーティクルを描画
        for particle in self.pachinko_particles:
            self._draw_pachinko_particle(particle)
        
        # ボーナスタイム表示
        if self.bonus_time_active:
            self._draw_bonus_time_ui()
    
    def _draw_mana_particle(self, particle: ManaParticle, alpha_multiplier: float = 1.0):
        """マナパーティクルの描画"""
        alpha = particle.life * alpha_multiplier
        if alpha <= 0:
            return
        
        x, y = int(particle.x), int(particle.y)
        size = int(particle.size * alpha)
        
        # 軌跡描画
        for i, (tx, ty) in enumerate(particle.trail_positions):
            trail_alpha = alpha * (i + 1) / len(particle.trail_positions) * 0.5
            if trail_alpha > 0.1:
                pyxel.pset(int(tx), int(ty), particle.color)
        
        # メインパーティクル描画
        if size >= 2:
            pyxel.circb(x, y, size, particle.color)
            if size >= 3:
                pyxel.circ(x, y, size - 1, particle.color)
        else:
            pyxel.pset(x, y, particle.color)
        
        # キラキラエフェクト
        if particle.sparkle_timer % 20 < 10:
            sparkle_x = x + int(math.cos(particle.sparkle_phase) * 3)
            sparkle_y = y + int(math.sin(particle.sparkle_phase) * 3)
            if 0 <= sparkle_x < 256 and 0 <= sparkle_y < 256:
                pyxel.pset(sparkle_x, sparkle_y, 7)  # 白いキラキラ
    
    def _draw_pachinko_particle(self, particle: PachinkoParticle):
        """パチンコパーティクルの描画"""
        if particle.life <= 0:
            return
        
        x, y = int(particle.x), int(particle.y)
        
        # パルス効果
        pulse_scale = 1.0 + math.sin(particle.pulse_timer * 0.3) * 0.3
        size = int(particle.size * particle.life * pulse_scale)
        
        if size >= 1:
            # 回転する星形エフェクト
            for i in range(4):
                angle = particle.angle + i * math.pi / 2
                end_x = x + int(math.cos(angle) * size)
                end_y = y + int(math.sin(angle) * size)
                if 0 <= end_x < 256 and 0 <= end_y < 256:
                    pyxel.line(x, y, end_x, end_y, particle.color)
            
            # 中心の円
            if size >= 2:
                pyxel.circ(x, y, max(1, size // 2), particle.color)
    
    def _draw_bonus_time_ui(self):
        """ボーナスタイム中のUI表示"""
        # 画面上部に「BONUS TIME!」表示
        bonus_text = "BONUS TIME!"
        text_x = 128 - len(bonus_text) * 2
        text_y = 20
        
        # 点滅効果
        if (self.bonus_time_timer // 10) % 2 == 0:
            # 背景
            pyxel.rect(text_x - 4, text_y - 2, len(bonus_text) * 4 + 8, 10, 8)
            # テキスト
            pyxel.text(text_x, text_y, bonus_text, 7)
        
        # 残り時間バー
        bar_width = int(200 * (self.bonus_time_timer / self.bonus_time_duration))
        pyxel.rect(28, 35, 200, 4, 0)  # 背景
        pyxel.rect(28, 35, bar_width, 4, 10)  # 残り時間
        pyxel.rectb(27, 34, 202, 6, 7)  # 枠
