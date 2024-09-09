import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from random import randint

# Set full-screen window size for mobile devices
Window.fullscreen = True

class monkey(Image):
    velocity = NumericProperty(0)
    jump_sound = None

    def on_touch_down(self, touch):
        if self.jump_sound:
            self.jump_sound.play()
        self.velocity = 170

    def move(self, dt):
        self.y += self.velocity * dt
        self.velocity -= 300 * dt

        if self.y < 0:
            self.y = 0
        elif self.y > Window.height - self.height:
            self.y = Window.height - self.height

class stick(Widget):
    def __init__(self, **kwargs):
        super(stick, self).__init__(**kwargs)
        self.gap_size = 200
        self.top_stick = Image(source='stick_top.png', size_hint=(None, None), size=(50, 400), allow_stretch=True, keep_ratio=False)
        self.bottom_stick = Image(source='stick_bottom.png', size_hint=(None, None), size=(50, 400), allow_stretch=True, keep_ratio=False)
        self.add_widget(self.top_stick)
        self.add_widget(self.bottom_stick)
        self.reset_position()

    def reset_position(self):
        bottom_height = randint(50, Window.height - self.gap_size - 50)
        self.bottom_stick.height = bottom_height
        self.bottom_stick.pos = (Window.width, 0)
        self.top_stick.height = Window.height - bottom_height - self.gap_size
        self.top_stick.pos = (Window.width, Window.height - self.top_stick.height)
        self.passed = False

    def move(self, dt):
        self.top_stick.x -= 200 * dt
        self.bottom_stick.x -= 200 * dt

        if self.top_stick.x < -self.top_stick.width:
            self.reset_position()

class ScrollingBackground(Widget):
    def __init__(self, **kwargs):
        super(ScrollingBackground, self).__init__(**kwargs)
        self.bg1 = Image(source='background.png', size_hint=(None, None), size=(Window.width, Window.height), allow_stretch=True, keep_ratio=False)
        self.bg2 = Image(source='background.png', size_hint=(None, None), size=(Window.width, Window.height), allow_stretch=True, keep_ratio=False)

        self.bg1.pos = (0, 0)
        self.bg2.pos = (Window.width, 0)

        self.add_widget(self.bg1)
        self.add_widget(self.bg2)

    def move(self, dt):
        self.bg1.x -= 100 * dt
        self.bg2.x -= 100 * dt

        if self.bg1.right <= 0:
            self.bg1.x = self.bg2.right
        if self.bg2.right <= 0:
            self.bg2.x = self.bg1.right

class Game(Widget):
    score = NumericProperty(0)
    background_music = None
    jump_sound = None
    score_sound = None
    collision_sound = None

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        
        # Load sounds
        self.background_music = SoundLoader.load('background_music.mp3')
        if self.background_music:
            self.background_music.loop = True

        self.jump_sound = SoundLoader.load('jump_sound.mp3')
        self.score_sound = SoundLoader.load('score_sound.mp3')
        self.collision_sound = SoundLoader.load('collision_sound.mp3')

        # Scrolling background
        self.background = ScrollingBackground()
        self.add_widget(self.background)
        
        # Create monkey
        self.monkey = monkey(source='monkey.png', size=(70, 70), pos=(100, Window.height / 2))
        self.monkey.jump_sound = self.jump_sound
        self.stick = stick()
        self.add_widget(self.monkey)
        self.add_widget(self.stick)

        # Create score label
        self.score_label = Label(text="Score: 0", font_size='20sp', pos=(0, Window.height - 50))
        self.add_widget(self.score_label)

    def start_game(self):
        if self.background_music:
            self.background_music.play()

        Clock.schedule_interval(self.update, 1 / 60)

    def update(self, dt):
        self.background.move(dt)
        self.monkey.move(dt)
        self.stick.move(dt)

        if self.monkey.collide_widget(self.stick.top_stick) or self.monkey.collide_widget(self.stick.bottom_stick):
            if self.collision_sound:
                self.collision_sound.play()
            self.game_over()

        if (self.monkey.x > self.stick.top_stick.x + self.stick.top_stick.width and not self.stick.passed):
            self.score += 1
            self.score_label.text = "Score: " + str(self.score)
            self.stick.passed = True
            if self.score_sound:
                self.score_sound.play()

    def game_over(self):
        Clock.unschedule(self.update)
        if self.background_music:
            self.background_music.stop()

        self.game_over_image = Image(source='game_over.png', size_hint=(None, None), size=(300, 300), pos=(50, 300))
        self.add_widget(self.game_over_image)

        self.continue_button = Button(text="Replay", size_hint=(None, None), size=(200, 50), pos=(100, 200))
        self.continue_button.background_color = (3, 1, 0, 1)
        self.continue_button.color = (1, 1, 1, 1)
        self.continue_button.bind(on_press=self.restart_game)
        self.add_widget(self.continue_button)

    def restart_game(self, instance):
        self.remove_widget(self.game_over_image)
        self.remove_widget(self.continue_button)
        self.score = 0
        self.score_label.text = "Score: 0"
        self.monkey.pos = (100, Window.height / 2)
        self.monkey.velocity = 0
        self.stick.reset_position()

        if self.background_music:
            self.background_music.play()

        Clock.schedule_interval(self.update, 1 / 60)

class FlappyWukongApp(App):
    def build(self):
        self.root = Widget()
        self.game = Game()
        self.start_button = Button(text="Start", size_hint=(None, None), size=(200, 50), pos=(100, Window.height / 3))
        self.start_button.background_color = (2,0 , 0, 1)
        self.start_button.color = (1, 1, 1, 1)
        self.start_button.bind(on_press=self.start_game)

        self.root.add_widget(self.game)
        self.root.add_widget(self.start_button)
        return self.root

    def start_game(self, instance):
        self.game.start_game()
        self.root.remove_widget(self.start_button)  # Correctly remove the start button from the root widget

if __name__ == '__main__':
    FlappyWukongApp().run()
