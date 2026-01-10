"""Ups, I dropped my jar with rubber balls."""


from multiprocessing import freeze_support
from random import randint, uniform
from lsd.strip import Strip, Animation
from lsd.visuals import bouncing_ball
from lsd.colors import random_tertiary


def bouncing():
    strip = Strip(300)

    previous_layer = strip
    for _ in range(5):
        anim = Animation(
            visual=bouncing_ball(
                leds=strip.n,
                color=random_tertiary(),
                tail=randint(2, 7),
                elasticity=uniform(0.8, 0.95),
                velocity=randint(-1, 0),
                pos=-randint(1, 10)),
            pixels=strip.n)

        previous_layer.bg = anim
        previous_layer = anim

    strip.play(30)


if __name__ == "__main__":
    freeze_support()
    bouncing()
