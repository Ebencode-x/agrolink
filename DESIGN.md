# AgroLink design rules

Applies to every template, script and message a user can see.

## Never
- Emoji, in the UI or in bot replies
- Em dashes or en dashes in visible text (use a comma, colon or period)
- Small badges, pills, chips, eyebrow labels, blinking dots
- Colored left bars on cards
- Gradient or diagonal hero backgrounds
- Glassmorphism outside login and register
- Stat counters showing low numbers
- Image placeholder boxes without a real file

## Always
- Horizontal rows, clear type hierarchy, large numbers
- Real photos of Tanzanian farmers, natural light, warm tones
- Rounded corners by default, square only where rows are split by lines
- Mobile first at 360px
- UI text in Kiswahili, English only for technical terms with no natural Kiswahili word
- Colors from tokens only: page #FFFFFF or #F8F9FA, text #1A1A1A, brand green #1B7A43, accent amber #D97706, success #16A34A, border #E5E7EB
- Playfair Display for headlines

## Process
- One area per PR, with screenshots before and after at 360px
- Bump the cache version in sw.js whenever static files change
