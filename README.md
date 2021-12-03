# Setup

1. Set `url` to the course overview page. I.E. https://codehs.com/student/XXXXXXXX/section/YYYYYYYY/

2. In configs, set `student_number` to the number in `X`'s' place (see example url above)
3. Set `section_number` to the number `Y`'s place.
4. `assignment_number` should be set to the assignment you want it to start on. This is found in the url, as the last number (after `/assignment/`)
5. `end_number` should be set to the assignment number that you want the script to end on.
6. `can_copy_paste`: Set to `True` if you are able to paste into the answer box. Otherwise, set it to `False`
7. `sign_in_with_google`: Set to `True` if you use google to sign in to CodeHS. Otherwise, set it to `False`.
