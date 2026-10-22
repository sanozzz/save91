from update_inputs import v
P = "founder's chosen plan (2026-09-30): 5% loss cover + gold"
UPDATES = {"inputs.csv": {
    "dlg_on": v(1, 1, 1, P, "REG-003, LEV-002", notes="Set to 0 to see the idea as briefed (savings + distribution only)."),
    "gold_on": v(1, 1, 1, P, "REG-022, REG-023, REG-024, LEV-041, LEV-043",
                 notes="Gold takes Rs 10 saves [LEV-039]; unregulated, framework under consultation, cannot back a loan. Set to 0 for the idea as briefed."),
}}
