"""motion.py - frame differencing."""
import cv2
import numpy as np

from motion import MotionDetector, draw_motion


def background():
    return np.full((540, 960, 3), 80, np.uint8)


def with_box(x, y, w=120, h=120):
    frame = background()
    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), -1)
    return frame


def test_first_frame_has_nothing_to_compare_with():
    assert MotionDetector().detect(background()) == []


def test_identical_frames_mean_no_motion():
    detector = MotionDetector()
    detector.detect(background())
    assert detector.detect(background()) == []


def test_a_moving_object_is_found_with_a_box_around_it():
    detector = MotionDetector()
    detector.detect(background())
    boxes = detector.detect(with_box(500, 300))
    assert len(boxes) == 1
    x, y, w, h = boxes[0]
    assert x <= 500 and y <= 300 and x + w >= 620 and y + h >= 420   # box covers the object


def test_small_changes_are_ignored_as_noise():
    detector = MotionDetector(min_area=1500)
    detector.detect(background())
    assert detector.detect(with_box(500, 300, 10, 10)) == []


def test_ignored_area_never_triggers_motion():
    """The phone app's clock (top-left) changes every second; that must not count."""
    detector = MotionDetector(ignore_box=(0, 0, 320, 200))
    detector.detect(background())
    assert detector.detect(with_box(10, 10, 190, 90)) == []


def test_motion_outside_the_ignored_area_still_counts():
    detector = MotionDetector(ignore_box=(0, 0, 320, 200))
    detector.detect(background())
    assert detector.detect(with_box(600, 300)) != []


def test_reset_forgets_the_previous_frame():
    detector = MotionDetector()
    detector.detect(background())
    detector.reset()
    assert detector.detect(with_box(500, 300)) == []  # treated as a fresh first frame


def test_a_change_of_frame_size_does_not_crash():
    detector = MotionDetector()
    detector.detect(np.full((540, 960, 3), 80, np.uint8))
    assert detector.detect(np.full((360, 640, 3), 80, np.uint8)) == []


def test_draw_motion_draws_green_rectangles():
    frame = background()
    draw_motion(frame, [(100, 100, 50, 50)])
    assert tuple(frame[100, 100]) == (0, 255, 0)    # BGR green on the box edge
    assert tuple(frame[300, 300]) == (80, 80, 80)   # the rest is untouched


def test_draw_motion_with_no_boxes_changes_nothing():
    frame = background()
    draw_motion(frame, [])
    assert np.array_equal(frame, background())
