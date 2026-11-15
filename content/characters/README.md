# Character backstories

One JSON file per fighter: `content/characters/<id>.json`. The `id` matches [`content/roster.json`](../roster.json) and the folder `art/characters/<id>/`.

The nine scaffold files are already named. Fill them in. Do not add a second copy of a fighter, and do not put the prose in `roster.json`. The roster only carries the select-screen name and a one-line placeholder. This folder carries the writing.

Plain text only. No Markdown. `taunt` and `winQuote` are one line each. `ending` is a short paragraph (one string). `rivals` is an array of other fighter **ids**, not display names.

## Fields

| Field | Type | What to write |
| --- | --- | --- |
| `id` | string | Stable id. Do not rename. |
| `name` | string | Display name. Keep in sync with the roster. |
| `section` | string | Percussion, Front ensemble, Woodwinds, Brass, or Color guard. |
| `instrument` | string | What they carry onto the field. |
| `fightingStyle` | string | How that instrument becomes a fighting style. The roster placeholder is a hint, not the finished line. |
| `personality` | string | A few sentences. |
| `rivals` | array of strings | Other fighter ids. Use `[]` when they have none yet. |
| `whyTheyFight` | string | The personal stake. |
| `taunt` | string | One line shouted at the start of a round. |
| `winQuote` | string | One line after they win a round. |
| `ending` | string | Arcade ending after they win the roster. |

## Shape

```json
{
  "id": "trumpet",
  "name": "Trumpet",
  "section": "Brass",
  "instrument": "Trumpet",
  "fightingStyle": "",
  "personality": "",
  "rivals": [],
  "whyTheyFight": "",
  "taunt": "",
  "winQuote": "",
  "ending": ""
}
```

Leave a string empty until it is written. An empty `rivals` array means none yet, not "rivals everyone."
