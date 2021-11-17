from manim import *

# Use our fork of manim_rubikscube!
from manim_rubikscube import *

# This also replaces the default colors
from solarized import *

import util

cube.DEFAULT_CUBE_COLORS = [BASE3, RED, GREEN, YELLOW, ORANGE, BLUE]


def bfs_circle_animations(
    center,
    iterations,
    label_angle=0.25 * PI,
    group=None,
    base_radius=0.9,
    radius_step=0.4,
):
    if group is None:
        group = Group()

    circle = Circle(color=RED, radius=base_radius).move_to(center)

    tex = MathTex(r"1", color=RED)

    tex.add_updater(
        lambda x: x.move_to(
            Point()
            .move_to(circle.get_right() + RIGHT * 0.4)
            .rotate(angle=label_angle, about_point=circle.get_center()),
        )
    )
    group.add(circle, tex)

    yield (GrowFromCenter(circle), FadeIn(tex))

    for i in range(1, iterations):
        c2 = circle.copy()
        group.add(c2)

        # This is needed so that the label follows properly during the animation
        # (we can't be moving `c2`, it has to be `circle`)
        circle, c2 = c2, circle

        tex2 = MathTex(str(i + 1), color=RED)

        c3 = Circle(color=RED, radius=base_radius + i * radius_step).move_to(center)

        yield (
            circle.animate.become(c3),
            c2.animate.set_color(GRAY),
            tex.animate.become(tex2),
        )

    tex.clear_updaters()


def generate_path_animations(center, angle, base_radius, radius_step, n_steps):
    spread = 0.3

    def get_radius(i):
        return base_radius + i * radius_step

    points = [Dot(color=RED).shift(center)]
    animations = [[Create(points[0])]]

    for i in range(n_steps):
        if i < n_steps - 1:
            cur_spread = np.arcsin(spread / get_radius(i))
            cur_angle = np.random.uniform(angle - cur_spread, angle + cur_spread)
        else:
            # Keep the last one centered to match the other side
            cur_angle = angle

        point = (
            Dot(color=RED)
            .shift(RIGHT * get_radius(i))
            .rotate_about_origin(cur_angle)
            .shift(center)
        )
        points.append(point)
        animations.append([Create(point)])

    for i in range(1, n_steps + 1):
        animations[i].append(
            Create(Line(points[i - 1].get_center(), points[i].get_center(), color=RED))
        )

    return points, animations


class BFSOneSide(ThreeDScene):
    def construct(self):
        """
        TODO: animace kde je nalevo scrambled kostka, napravo složená, přidáváme
        “slupky” kolem scrambled, vnější slupka se vzdáleností 20 už obsahuje
        složenou kostku.

        Ztratí se slupky až na prvních 10, ty tu kostku neobsahují.

        Ztratí se všechny slupky, ukážeme je kolem složené (do vzdálenosti 10).

        Ukázat slupky z obou stran, musí se protínat

        TODO: nějak navázat na následující animaci, ideálně ale rozdělit aby se
        to snáz renderovalo
        """
        pass


class CubeMITM(ThreeDScene):
    def construct(self):
        """
        Meet in the middle.
        TODO: změnit, aby odpovídalo textu:

        Ok, why is this useful? Well, instead of starting on one side and trying
        to reach the other, we can actually search from both sides at once and
        stop once we meet in the middle. By that we mean searching until the two
        balls intersect for the first time. When that happens, there is a
        configuration for which we know the fastest way to reach it both from
        the scrambled cube and from the solved one. Then we simply connect these
        two partial paths to get the best solution.
        """
        self.camera.set_focal_distance(20000.0)
        cube_distance = 8
        cube_from = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            LEFT * cube_distance / 2
        )
        cube_to = RubiksCube(cubie_size=0.3, rotate_nicely=True).shift(
            RIGHT * cube_distance / 2
        )
        util.scramble_to_feliks(cube_from)

        self.add(cube_from, cube_to)
        self.wait()

        base_radius = 0.9
        radius_step = 0.3
        # TODO: co s tim, ze cesta ma 18 kroku ale polomer koule ma byt 10?
        n_steps = 9

        group_from = Group(cube_from)
        group_to = Group(cube_to)

        for anims_from, anims_to in zip(
            bfs_circle_animations(
                cube_from.get_center(),
                n_steps,
                label_angle=0.25 * PI,
                group=group_from,
                base_radius=base_radius,
                radius_step=radius_step,
            ),
            bfs_circle_animations(
                cube_to.get_center(),
                n_steps,
                label_angle=0.75 * PI,
                group=group_to,
                base_radius=base_radius,
                radius_step=radius_step,
            ),
        ):
            self.play(*anims_from, run_time=1 / 3)
            self.play(*anims_to, run_time=1 / 3)

        self.wait()

        ############ Move the cubes together ############

        coef = 0.5 * cube_distance - (base_radius + radius_step * (n_steps - 1))
        self.play(
            group_from.animate.shift(RIGHT * coef), group_to.animate.shift(LEFT * coef)
        )

        self.wait()

        ############ Generate the path ############

        points_from, path_anims_from = generate_path_animations(
            cube_from.get_center(), 0, base_radius, radius_step, n_steps
        )
        points_to, path_anims_to = generate_path_animations(
            cube_to.get_center(), PI, base_radius, radius_step, n_steps
        )

        for anims_from, anims_to in zip(path_anims_from, path_anims_to):
            self.play(*(anims_from + anims_to), run_time=0.5)

        self.wait()

        ############ Walk it ############
        self.bring_to_front(cube_from)

        points_both = points_from[1:-1] + points_to[::-1]

        self.play(
            cube_from.animate.move_to(points_from[0].get_center() + DOWN),
            FadeOut(cube_to),
        )

        for i, move in zip(range(len(points_both)), util.FELIKS_UNSCRAMBLE_MOVES):
            self.play(
                CubeMove(cube_from, move, points_both[i].get_center() + DOWN),
                run_time=0.5,
            )
            # if i == 4:
            #     break

        self.wait()


class MemoryIssues(ThreeDScene):
    def construct(self):
        """
        TODO: vymyslet animaci k tomuhle:

        So in terms of time, we’re in the clear. But another issue arises if we
        try to actually implement this idea: memory. Storing 10^10 cube
        configurations would require about XYZ GB, a bit too much for our poor
        laptops. This means that we need to use some additional trickery to make
        the code work. But it can be done - if you’re curious, check out the
        code linked in the video description. We also include a bit about the
        state-of-the-art solving algorithms. Those algorithms also use the meet
        in the middle idea, but they also exploit some more specific properties
        of the cube graph, which allows them to be much faster than our simple
        meet in the middle search.

        The trick that we have used is called the meet in the middle trick, for
        obvious reasons. In this special instance, it is also called
        bidirectional search. The only property of the cube graph that we
        exploited is that the number of explored nodes grows very rapidly.
        Graphs with this property are more common than you think, not just
        rubik’s cube graph and friendship networks. Again, more in the video
        description!
        """
        pass