This codebase now includes the code for the website [www.cubecana.com](https://www.cubecana.com/) which includes most of the functionality described below and more in a more user-friendly format! I recommend you start there, and come back if you feel you need more.


I think I just created the fastest, easiest way to draft Lorcana online. If there is an easier or faster way to draft, please let me know at zacharysmith4989@gmail.com !

A video tutorial on how to draft as either a non-host participant or a host: https://www.youtube.com/watch?v=lm1xPenIKQg

If you'd rather read:

In order to draft as a non-host participant, you only need to:
1. Pick your cards using Draftmancer, then
2. copy & paste into dreamborn.ink , from where you'll probably export to pixelborn.

The host(s) will need to:
1. Import the draft list from dreamborn into Draftmancer:
    1. Export the draft list from dreamborn to clipboard,
    2. paste from clipboard into the bottom of a Draftmancer Custom Card List template,
    3. upload to Draftmancer as a Custom Card List, then
2. host the draft in Draftmancer (see either the video tutorial above or 5:00-9:24 here: https://www.youtube.com/watch?v=dbYUgwbHwxU&t=745s&ab_channel=JankDiverGaming ).

Here is the template: https://github.com/ZacharyRSmith/dreamborn_to_draftmancer/blob/main/simple_template.draftmancer.txt

To import a drafted deck into dreamborn.ink:
1. In Draftmancer, copy drafted deck to clipboard using 'Export > CARD NAMES'.
2. In dreamborn.ink, go to 'Deck Builder',
3. select 'Menu > Import',
4. paste clipboard into import text field,
5. (OPTIONALLY, to remove sideboard) remove the bottom half that is separated from the top half by an empty line (the bottom half is your 'sideboard'), then
6. select 'Import'.


# Details

Using lorcana-api.com data, each card is assigned an ink cost, a rarity


# Potential Enhancements
- Add a way for people to set packs by rarity automatically?
- Add default lists for retail sets 1-5
- host this somewhere so people can use it on a website!?

## How to support sealed?

To simplify for now, I'll assume the 12th, foil card is just another rare or higher card, and that packs have random color and ink costs (idk whether or not they do).

Change the template to have:

```
[RareOrHigherSlot(3)]
[UncommonSlot(3)]
[CommonSlot(6)]
```

Change the script to read in all 612 cards using https://dreamborn.ink/decks/Xk1wFdToEUoyeb1tvU6V . Using rarity data from lorcana-api.com , put card into appropriate slot section. Number of each card can be determined by script, but more likely you want to set Draftmancer's `withReplacement` to true such that Draftmancer has an unlimited supply of each card?

Specific sets can be selected by changing the script to filter cards by set using data from lorcana-api.com .


# Testing

I tested this on all 1020 cards using the exports in dreamborn_export-examples (up through set 5 on Sept. 10, 2024)

I successfully exported that into the template, uploaded to Draftmancer, drafted 24 cards, then imported to dreamborn.
