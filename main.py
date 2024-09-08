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

# Configure window size
Window.size = (400, 600)

class monkey(Image):
    velocity = NumericProperty(0)
    jump_sound = None

    def on_touch_down(self, touch):
        # Play jump sound when screen is touched
        if self.jump_sound:
            self.jump_sound.play()
        # monkey jumps up when the screen is touched
        self.velocity = 170

    def move(self, dt):
        # Move the monkey up or down
        self.y += self.velocity * dt
        self.velocity -= 300 * dt  # Gravity affects the monkey

        # Limit the monkey so it doesn't fall too low or fly too high
        if self.y < 0:
            self.y = 0
        elif self.y > Window.height - self.height:
            self.y = Window.height - self.height

class stick(Widget):
    def __init__(self, **kwargs):
        super(stick, self).__init__(**kwargs)
        # Gap between sticks for the monkey to pass through
        self.gap_size = 200
        # Configure top and bottom stick images with allow_stretch and keep_ratio
        self.top_stick = Image(source='stick_top.png', size_hint=(None, None), size=(50, 400), allow_stretch=True, keep_ratio=False)
        self.bottom_stick = Image(source='stick_bottom.png', size_hint=(None, None), size=(50, 400), allow_stretch=True, keep_ratio=False)
        self.add_widget(self.top_stick)
        self.add_widget(self.bottom_stick)
        self.reset_position()

    def reset_position(self):
        # Calculate random height for the bottom stick
        bottom_height = randint(50, Window.height - self.gap_size - 50)
        # Set height and position of bottom and top sticks
        self.bottom_stick.height = bottom_height
        self.bottom_stick.pos = (Window.width, 0)
        self.top_stick.height = Window.height - bottom_height - self.gap_size
        self.top_stick.pos = (Window.width, Window.height - self.top_stick.height)
        self.passed = False  # Reset the passed state

    def move(self, dt):
        # Move sticks from right to left
        self.top_stick.x -= 200 * dt
        self.bottom_stick.x -= 200 * dt

        # When the stick goes off the screen, reset position and create random height
        if self.top_stick.x < -self.top_stick.width:
            self.reset_position()

class ScrollingBackground(Widget):
    def __init__(self, **kwargs):
        super(ScrollingBackground, self).__init__(**kwargs)
        # Create two background images for scrolling effect
        self.bg1 = Image(source='background.png', size_hint=(None, None), size=(Window.width, Window.height), allow_stretch=True, keep_ratio=False)
        self.bg2 = Image(source='background.png', size_hint=(None, None), size=(Window.width, Window.height), allow_stretch=True, keep_ratio=False)
        
        # Set initial positions of two backgrounds
        self.bg1.pos = (0, 0)
        self.bg2.pos = (Window.width, 0)
        
        # Add backgrounds to the interface
        self.add_widget(self.bg1)
        self.add_widget(self.bg2)

    def move(self, dt):
        # Move both backgrounds from right to left
        self.bg1.x -= 100 * dt  # Background scrolling speed
        self.bg2.x -= 100 * dt
        
        # When the background goes off the screen, reset position for continuous scrolling
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
            self.background_music.play()

        self.jump_sound = SoundLoader.load('jump_sound.mp3')
        self.score_sound = SoundLoader.load('score_sound.mp3')  # Load score sound
        self.collision_sound = SoundLoader.load('collision_sound.mp3')  # Load collision sound

        # Add scrolling background
        self.background = ScrollingBackground()
        self.add_widget(self.background)
        
        # Create monkey object
        self.monkey = monkey(source='monkey.png', size=(70, 70), pos=(100, Window.height / 2))
        self.monkey.jump_sound = self.jump_sound  # Assign jump sound to monkey
        # Create stick
        self.stick = stick()
        # Add monkey and stick to the game interface
        self.add_widget(self.monkey)
        self.add_widget(self.stick)

        # Create label to display score
        self.score_label = Label(text="Score: 0", font_size='20sp', pos=(0, Window.height - 50))
        self.add_widget(self.score_label)

        # Start updating the game at 60 FPS
        Clock.schedule_interval(self.update, 1/60)

    def update(self, dt):
        # Move scrolling background
        self.background.move(dt)
        
        # Move monkey and stick
        self.monkey.move(dt)
        self.stick.move(dt)

        # Check for collision between monkey and sticks
        if self.monkey.collide_widget(self.stick.top_stick) or self.monkey.collide_widget(self.stick.bottom_stick):
            if self.collision_sound:
                self.collision_sound.play()
            self.game_over()

        # Update score when monkey passes through stick
        if (self.monkey.x > self.stick.top_stick.x + self.stick.top_stick.width and 
            not self.stick.passed):
            self.score += 1
            self.score_label.text = "Score: " + str(self.score)
            print("Score:", self.score)
            self.stick.passed = True
            
            # Play score sound
            if self.score_sound:
                self.score_sound.play()

    def game_over(self):
        print("Game Over")
        Clock.unschedule(self.update)  # Stop game when collision occurs

        # Stop background music
        if self.background_music:
            self.background_music.stop()

        # Display "Game Over" image
        self.game_over_image = Image(source='game_over.png', size_hint=(None, None), size=(300, 300), pos=(50, 350))
        self.add_widget(self.game_over_image)

        # Create "Replay" button to restart the game
        self.continue_button = Button(text="Replay", size_hint=(None, None), size=(200, 50), pos=(100, 200))
        self.continue_button.background_color = (3, 1, 0, 1)  # Button background color
        self.continue_button.color = (1, 1, 1, 1)  # Button text color (White)
        self.continue_button.bind(on_press=self.restart_game)
        self.add_widget(self.continue_button)

    def restart_game(self, instance):
        # Reset game
        self.remove_widget(self.game_over_image)
        self.remove_widget(self.continue_button)
        self.score = 0
        self.score_label.text = "Score: 0"
        self.monkey.pos = (100, Window.height / 2)
        self.monkey.velocity = 0
        self.stick.reset_position()
        
        # Restart background music
        if self.background_music:
            self.background_music.play()

        Clock.schedule_interval(self.update, 1/60)

class FlappyWukongApp(App):
    def build(self):
        return Game()

if __name__ == '__main__':
    FlappyWukongApp().run()
