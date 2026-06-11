# Sample incidents seeded into an empty database at startup so the dashboard is not
# blank on a fresh deploy. Each set is written to look like a real, full-length guard
# account (the five W's and the one H) and is built to exercise the report: some genuine
# conflicts, some near-duplicate wording that should NOT be flagged, and at least one
# incident dimension nobody covered. The "label" on each report is the guard's name; the
# conflicts section refers to guards by that name.

SAMPLES = [
    {
        "title": "After-Hours Trespasser at East Loading Dock",
        "reports": [
            {
                "label": "Officer D. Reyes",
                "body": (
                    "On Tuesday, March 4, at approximately 11:05 PM, I was conducting my "
                    "scheduled perimeter patrol on the east side of the property when I "
                    "observed an adult male standing near the closed east loading dock, "
                    "between the dumpster enclosure and the roll-up door. He was not wearing "
                    "a visitor badge or a contractor vest, and the dock had been secured and "
                    "locked at 8:00 PM per the nightly checklist, so no one was authorized to "
                    "be in that area at that hour.\n\n"
                    "The subject appeared to be a white male, roughly 5'10\" to 6'0\", medium "
                    "build, wearing a dark hooded sweatshirt with the hood up and dark jeans. "
                    "I could not see his face clearly because of the hood and the low light. "
                    "I announced myself and asked him to stop and identify himself. He did not "
                    "respond and immediately began walking quickly toward the north fence "
                    "line. I notified dispatch by radio at 11:07 PM, requested backup, and "
                    "followed at a safe distance, keeping him in view but not attempting to "
                    "detain him on my own.\n\n"
                    "The subject reached the perimeter fence near the northeast corner, "
                    "climbed over it, dropped down on the far side, and continued north on "
                    "foot off the property. I did not see him carrying anything in his hands. "
                    "After he left I checked the dock door and the surrounding area; the door "
                    "was still secured and I saw no signs of forced entry or missing property "
                    "at that time. I logged the event and remained on scene until relieved."
                ),
            },
            {
                "label": "Officer K. Patel",
                "body": (
                    "At about 11:20 PM on March 4 I responded to Officer Reyes's radio call "
                    "regarding an unidentified person at the east loading dock. I left the "
                    "main gate and drove the patrol cart around the south side of the building "
                    "to cut off the route toward the public parking structure. By the time I "
                    "had eyes on the area, the subject was already at the fence at the "
                    "northeast corner.\n\n"
                    "I watched him go over the fence and saw that he was carrying a dark "
                    "backpack over one shoulder as he climbed. After he came down on the other "
                    "side he ran across the access road toward the public parking structure on "
                    "the opposite side of the street, not north along the fence. I tried to "
                    "follow him to the street but lost sight of him when he entered the "
                    "parking-structure stairwell. I never made contact with the subject and "
                    "did not get a clear look at his face.\n\n"
                    "I returned to the dock to assist Officer Reyes and we walked the fence "
                    "line together. I agree the dock door was secured. I did not personally "
                    "check whether anything was missing from the dock."
                ),
            },
            {
                "label": "Officer S. Brennan",
                "body": (
                    "I was monitoring the CCTV feeds in the camera room during the overnight "
                    "shift on March 4. At around 11:06 PM I noticed movement on the east dock "
                    "camera and saw a person in dark clothing near the roll-up door. I radioed "
                    "the floor that I had the subject on camera and tracked him across two "
                    "camera zones as he moved from the dock toward the northeast fence.\n\n"
                    "The camera covering the fence corner has a partial blind spot because of "
                    "a light fixture, so I lost the subject for several seconds right at the "
                    "fence and did not personally see him go over it. I did note that, before "
                    "moving off, the subject stopped briefly at the dock and appeared to "
                    "crouch or reach toward the base of the door, though the image is not "
                    "clear enough for me to say what he was doing. I saved the relevant "
                    "camera clips to the incident folder with timestamps. I could not tell "
                    "from the footage whether he was carrying a bag."
                ),
            },
        ],
    },
    {
        "title": "Level 2 Parking Garage Vehicle Break-In",
        "reports": [
            {
                "label": "Officer J. Alvarez",
                "body": (
                    "On Friday, March 7, at approximately 3:15 PM, a tenant, Ms. Coleman from "
                    "the 4th-floor office suite, flagged me down on Level 2 of the parking "
                    "garage and reported that the driver's-side window of her silver sedan "
                    "had been smashed and a laptop bag taken from the back seat. I was on foot "
                    "patrol coming up the Level 2 ramp when she called out to me.\n\n"
                    "As I approached the vehicle I saw one individual wearing a red baseball "
                    "cap and a gray jacket running away from the area toward the north "
                    "stairwell. I was not able to catch up to him and he disappeared into the "
                    "stairwell. I secured the immediate scene around the vehicle, asked the "
                    "tenant not to touch the broken glass, and took her initial statement. "
                    "Broken glass was on the ground next to the driver's door.\n\n"
                    "I notified dispatch, requested that the property manager be contacted, "
                    "and advised the tenant to file a police report for the stolen laptop bag. "
                    "I remained with the vehicle until the property manager arrived."
                ),
            },
            {
                "label": "Officer M. Whitfield",
                "body": (
                    "On March 7 I was assigned to the security camera room. At around 3:10 PM, "
                    "just before the break-in on Ms. Coleman's vehicle was reported, I "
                    "observed two individuals on the Level 2 camera standing close to a silver "
                    "vehicle in the row near the elevator lobby. One of them was wearing a "
                    "light-colored cap.\n\n"
                    "A few moments later both individuals moved quickly away from the vehicle "
                    "and left together down the south stairwell at the far end of the level. I "
                    "radioed Officer Alvarez with what I was seeing. From the camera angle I "
                    "could see the driver's-side window appeared shattered. I saved the "
                    "footage covering roughly 3:05 PM to 3:20 PM to the incident folder. I did "
                    "not have a camera angle that showed either person's face clearly."
                ),
            },
        ],
    },
    {
        "title": "Third-Floor Fire Alarm Activation (Overnight)",
        "reports": [
            {
                "label": "Officer R. Donnelly",
                "body": (
                    "At 2:40 AM on Sunday, March 9, the fire alarm panel indicated activation "
                    "of a smoke detector on the third floor, east wing. I proceeded to the "
                    "third floor to investigate. I did not find any visible smoke or flames, "
                    "but I did notice a faint burnt odor near the third-floor break room and "
                    "kitchen area.\n\n"
                    "I held the floor and waited for the fire department, who arrived at "
                    "approximately 2:55 AM and conducted a sweep of the east wing. They found "
                    "no active fire and cleared the building at about 3:20 AM. After they "
                    "cleared it, I reset the alarm panel and logged the event. My impression "
                    "is that the alarm may have been triggered by something in the kitchen, "
                    "but the cause was not confirmed by the fire department."
                ),
            },
            {
                "label": "Officer A. Kim",
                "body": (
                    "An alarm sounded on the third floor in the early hours of March 9. I was "
                    "on the lower floors when it activated and immediately began sweeping the "
                    "building for occupants. I located and escorted three members of the "
                    "overnight cleaning crew, who were working on the second and third floors, "
                    "out to the designated muster point in the front parking lot.\n\n"
                    "I accounted for all three by name against the after-hours sign-in sheet. "
                    "The fire department checked the floor and found nothing burning. Once the "
                    "all-clear was given, the cleaning staff were allowed back in to collect "
                    "their equipment. While sweeping the lower floors I did not notice any "
                    "smell of smoke or burning."
                ),
            },
        ],
    },
]
