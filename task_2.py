
"""
Сніжинка Коха з рекурсією.
Користування:
    python koch_snowflake.py --level 4 --size 300 --speed 0
"""

import argparse
import sys
import turtle


def koch_segment(t: turtle.Turtle, length: float, level: int) -> None:
    """Рекурсивно малює один відрізок кривої Коха."""
    if level == 0:
        t.forward(length)
        return
    length /= 3.0
    koch_segment(t, length, level - 1)
    t.left(60)
    koch_segment(t, length, level - 1)
    t.right(120)
    koch_segment(t, length, level - 1)
    t.left(60)
    koch_segment(t, length, level - 1)


def koch_snowflake(t: turtle.Turtle, length: float, level: int) -> None:
    """Малює сніжинку Коха (3 сторони)."""
    for _ in range(3):
        koch_segment(t, length, level)
        t.right(120)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Рекурсивна сніжинка Коха (turtle)."
    )
    p.add_argument("--level", "-l", type=int, default=3,
                   help="Рівень рекурсії (0..8 рекомендовано). За замовчуванням: 3")
    p.add_argument("--size", "-s", type=float, default=300,
                   help="Довжина сторони початкового трикутника (пікселі). За замовчуванням: 300")
    p.add_argument("--speed", type=int, default=0,
                   help="Швидкість черепахи (0—найшвидше, 1..10). За замовчуванням: 0")
    p.add_argument("--bg", type=str, default="white",
                   help="Колір фону (напр., white, black).")
    p.add_argument("--color", type=str, default="blue",
                   help="Колір лінії.")
    return p.parse_args()


def main() -> int:
    args = parse_args()

    if args.level < 0:
        print("Помилка: рівень рекурсії має бути ≥ 0")
        return 1
    if args.level > 8:
        print("Увага: дуже високий рівень може бути повільним. Спробуй 6–8.")
        # не завершуємо — дозволяємо користувачу експериментувати

    # Налаштування екрану
    screen = turtle.Screen()
    screen.title(f"Koch Snowflake — level {args.level}")
    screen.bgcolor(args.bg)

    t = turtle.Turtle(visible=False)
    t.speed(args.speed)
    t.color(args.color)
    t.pensize(2)

    # Центруємо фігуру: зміщуємося вліво-вниз
    # Висота рівностороннього трикутника: size * sqrt(3)/2 ≈ 0.866*size
    height = 0.866 * args.size
    t.penup()
    t.goto(-args.size / 2.0, -height / 3.0)  # трошки нижче центру для гарного вміщення
    t.pendown()

    koch_snowflake(t, args.size, args.level)

    # Залишаємо вікно відкритим до кліку
    t.hideturtle()
    turtle.done()
    return 0


if __name__ == "__main__":
    sys.exit(main())
