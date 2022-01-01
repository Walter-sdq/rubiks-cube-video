import itertools

from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util


cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]

#https://colorswall.com/palette/171
# TODO vyrenderovat s těmahle barvama aspoň jednu kostku někde
# cube.DEFAULT_CUBE_COLORS = ["#ffffff", "#b71234", "#009b48", "#ffd500", "#ff5800", "#0046ad"]


class Logo(ThreeDScene):
    def construct(self):
        text_color = GRAY
        buffer_h = 2.7
        buffer_v = 1.3  # pripadne: 1.5
        row_shift = 0.35  # pripadne: 0

        a = []
        for i in range(3):
            row = []
            for j in range(3):
                cur = Tex(r"log", color=text_color)
                cur.scale(4).shift(
                    (j * buffer_h + i * row_shift) * RIGHT + i * buffer_v * DOWN
                )
                row.append(cur)

            a += row

        group = Group(*a)
        group.move_to(ORIGIN)

        if False:
            w, h = 14, 8.2
            w = h
            bg = Polygon(
                np.array([-w / 2, h / 2, 0]),
                np.array([w / 2, h / 2, 0]),
                np.array([-w / 2, -h / 2, 0]),
                color=BASE02,
                fill_opacity=1,
            )

            self.add(bg, *a)


class ChannelIntro(ThreeDScene):
    def construct(self):
        text_color = GRAY

        buffer = 0.7

        hlasek = Tex(r"\textbf{Filip Hlásek}: code", color=text_color).shift(
            0 * DOWN * buffer
        )
        rozhon = Tex(
            r"\textbf{Václav Rozhoň}: script, animation", color=text_color
        ).shift(
            DOWN * buffer
        )
        volhejn = Tex(
            r"\textbf{Václav Volhejn}: voice, script, animation",
            color=text_color,
        ).shift(2 * DOWN * buffer)


        names = Group(rozhon, volhejn, hlasek)
        names.shift(2 * DOWN + LEFT)

        volhejn.align_to(names, LEFT)
        rozhon.align_to(names, LEFT)
        hlasek.align_to(names, LEFT)

        channel_name = Tex(r"polylog", color=text_color)
        channel_name.scale(4).shift(1 * UP)

        run_time = Write(channel_name).run_time
        self.play(
            Write(volhejn, run_time=run_time),
            Write(rozhon, run_time=run_time),
            Write(hlasek, run_time=run_time),
            Write(channel_name, run_time=run_time),
        )

        self.wait(3)

        self.play(
            Unwrite(volhejn, reverse=True),
            Unwrite(rozhon),
            Unwrite(hlasek),
            Unwrite(channel_name),
            run_time=1,
        )
        self.wait(1)


class MoveDefinition(util.RubikScene):
    def construct(self):
        """
        Co počítáme jako jeden move?

        What counts as one move? Say that for simplicity, we will assume that we
        never rotate the cube as a whole, so the middle cubies will always stay
        in the same place. Then, a move only rotates the sides of the cube: the
        top and bottom, the left and right, and the front and back. Each can be
        rotated to three new positions, hence 18 total possibilities.
        """
        faces = "UDLRFB"
        positions = []

        for dy in range(3):
            for dx in range(-3, 3):
                positions.append([dx + 0.5, -dy - 2, 0])

        first_cube = RubiksCube(cubie_size=1)

        self.play(FadeIn(first_cube))
        self.play(Rotate(first_cube, 2 * PI, UP), run_time=3)

        self.play(first_cube.animate.scale(0.5))

        grid_spacing = 2

        cubes = [RubiksCube(cubie_size=0.5) for i in range(len(faces))]

        self.add(*cubes)
        self.remove(first_cube)

        self.play(
            *[
                cube.animate.shift(RIGHT * grid_spacing * (i - 2.5))
                for i, cube in enumerate(cubes)
            ]
        )

        self.wait()

        self.play(
            *[CubeMove(cube, face + "4") for cube, face in zip(cubes, faces)],
            run_time=3,
        )

        self.wait()

        anims = []

        for y in [-1, 1]:
            for i, face in enumerate(faces):
                cubes.append(
                    RubiksCube(rotate_nicely=True, cubie_size=0.5).shift(
                        RIGHT * grid_spacing * (i - 2.5)
                    )
                )
                anims.append(cubes[-1].animate.shift(UP * grid_spacing * y))

        self.add(*cubes)

        self.play(*anims)
        self.wait()

        anims = []

        for j in [2, 0, 1]:
            for i, face in enumerate(faces):
                anims.append(CubeMove(cubes[j * 6 + i], face + ["", "2", "'"][j]))

        self.play(LaggedStart(*anims))
        self.wait(2)


class FeliksVsOptimal(util.RubikScene):
    def construct(self):
        """
        For example, with this definition the position that Mr. Zemdegs solved
        can be solved in 18 moves, although Mr. Zemdegs’s solution was of course
        different and used 44 moves.
        """

        cube_distance = 7

        cube_actual = RubiksCube(cubie_size=0.75, rotate_nicely=False).shift(
            LEFT * cube_distance / 2
        )
        cube_best = RubiksCube(cubie_size=0.75, rotate_nicely=False).shift(
            RIGHT * cube_distance / 2
        )

        buff = 1
        text_actual = (
            Tex("Feliks Zemdegs", color=GRAY)
            .scale(1.5)
            .next_to(cube_actual, direction=UP, buff=buff)
        )
        counter_actual = (
            Integer(0, color=GRAY)
            .scale(1.5)
            .next_to(cube_actual, direction=DOWN, buff=buff)
        )
        text_best = (
            Tex("Omniscient being", color=GRAY)
            .scale(1.5)
            .next_to(cube_best, direction=UP, buff=buff)
        )
        counter_best = (
            Integer(0, color=GRAY)
            .scale(1.5)
            .next_to(cube_best, direction=DOWN, buff=buff)
        )

        self.add(text_actual, text_best, counter_actual, counter_best)

        for cube in [cube_best, cube_actual]:
            util.scramble_to_feliks(cube)

            # Rotate to get Feliks' POV
            cube.rotate(PI / 2, RIGHT)
            cube.rotate(PI / 2, UP)

            # "rotate nicely"
            cube.rotate(15 * DEGREES, axis=np.array([1, 0, 0]))
            cube.rotate(15 * DEGREES, axis=np.array([0, 1, 0]))

        self.add(cube_best, cube_actual)
        self.wait()

        for i, (move_actual, move_best) in enumerate(
            itertools.zip_longest(
                util.FELIKS_ACTUAL_SOLUTION_MOVES, util.FELIKS_UNSCRAMBLE_MOVES
            )
        ):
            anims_cur = [cube_actual.animate.do_move(move_actual)]
            if move_best is not None:
                anims_cur += [cube_best.animate.do_move(move_best)]
            self.play(*anims_cur, run_time=(10 / (15 + i)))

            counter_actual.set_value(i + 1).set_color(GRAY)
            if move_best is not None:
                counter_best.set_value(i + 1).set_color(GRAY)

        self.wait()
        self.play(FadeIn(Tex("cube20.org", color=GRAY)))
        self.wait()


class CubeGraph(util.RubikScene):
    def construct(self):
        """
        TODO: ukázat co myslíme grafem kostky v tomto případě. Ukázat malou část
        grafu (nejspíš ani neukazovat všech 18 hran z vrcholu), každý vrchol
        jedna kostka. Pak v něm vyznačit cestu z nějakého stavu do složeného,
        nejspíš něco triviálního o délce 2.

        In this case, the possible configurations of the cube form the nodes of
        a vast network, with two nodes being connected if there is a move from
        one configuration to the other. In computer science, we call such
        networks graphs and the connections edges. Thinking in terms of graphs
        is a common trick, since it can stand for a road network, or friendships
        on a social network, or, in our case an abstract network of
        configurations.

        So let’s say we want to solve our cube with as few moves as possible. In
        the language of graphs, this amounts to finding the shortest path from
        the scrambled configuration to the solved one.

        So how can we find the shortest path? The first solution that comes to
        mind is to take the scrambled configuration and do what is also called
        the breadth first search algorithm. Simply speaking, this algorithm
        explores all possible configurations from the scrambled one in the order
        of their distance to that configuration. We are searching until we
        encounter the solved configuration.
        """
        # TODO: najit zajimavejsi graf, ve kterem existuji dve cesty (dve reseni)
        # ktere se netrivialne lisi a jedna je rychlejsi.
        vertices = [
            1,  # solved
            2,  # R
            3,  # L2
            4,  # L2 R
            5,  # R U'
        ]
        edges = [(1, 2), (1, 3), (2, 4), (3, 4), (5, 2)]
        g = Graph(
            vertices,
            edges,
            vertex_type=RubiksCube,
            vertex_config={
                "cubie_size": 0.3,
            },
            edge_config={
                "color": GRAY,
                "shade_in_3d": True,  # Needed to keep the edges behind the cube
            },
            layout="kamada_kawai",
        )
        g[2].do_move("R")
        g[3].do_move("L2")
        g[4].do_move("L2").do_move("R")
        g[5].do_move("R").do_move("U'")

        # self.play(Create(g))
        self.add(g)

        self.wait()

        self.play(
            g[1].animate.move_to([1, 1, 0]),
            g[2].animate.move_to([-1, 1, 0]),
            g[3].animate.move_to([1, -1, 0]),
            g[4].animate.move_to([-1, -1, 0]),
        )
        self.wait()

        # TODO: zvyraznit nejkratsi cestu

        # TODO: vizualizovat BFS (podobne jako v prvnim videu)


class NumberOfStates(Scene):
    def construct(self):
        """
        So can this work? Let’s try to find some basic parameters of Rubik’s
        cube. A quick Wikipedia search shows that the number of its states
        reachable from the starting one is exactly 43252003274489856000 which is
        roughly 10^20.

        So in the worst case, our algorithm will have to explore about 10^20
        cube configurations until it finds a solution. That’s a lot! A computer
        can explore roughly 10^6 configurations per second, so this would take
        10^14 seconds, or millions of years. The limit of what we can possibly
        explore with a normal computer in reasonable time is around 10^10 cube
        states, the time to explore this number of configurations should be,
        say, a few hours. Although 10^10 is also a huge number it is laughably
        small if you compare it with 10^20.
        """
        parts_s = ["43", "252", "003", "274", "489", "856", "000"]
        scale_coef = 1.1
        scale_base = 2.0

        parts = [
            Tex(p, color=GRAY).scale(scale_base * scale_coef ** (len(parts_s) - 1 - i))
            for i, p in enumerate(parts_s)
        ]
        group = Group()

        for i, part in enumerate(parts):
            if i > 0:
                part.next_to(
                    parts[i - 1], buff=0.3 * scale_coef ** (len(parts_s) - 1 - i)
                )
            self.play(Write(part))
            group.add(part)
            if i > 0:
                self.play(
                    group.animate.shift(-group.get_center()).scale(1 / scale_coef),
                    run_time=0.3,
                )

        self.wait()

        ten_to_twenty = MathTex(r"\approx 10^{20}", color=GRAY).scale(scale_base)
        ten_to_twenty.next_to(group, direction=DOWN).align_to(group, RIGHT)
        self.play(Write(ten_to_twenty))

        self.wait()
        self.play(group.animate.shift(UP * 2.5), ten_to_twenty.animate.shift(UP * 2.5))
        self.wait()

        ten_to_ten_decimal = (
            MathTex(r"10\,000\,000\,000", color=GRAY)
            .scale(scale_base)
            .align_to(group, RIGHT)
            .shift(DOWN * 1.3)
        )
        ten_to_ten_scientific = (
            MathTex(r"= 10^{10}", color=GRAY)
            .scale(scale_base)
            .next_to(ten_to_ten_decimal, direction=DOWN)
            .align_to(group, RIGHT)
        )

        self.play(Write(ten_to_ten_decimal))
        self.play(Write(ten_to_ten_scientific))
        self.wait()
