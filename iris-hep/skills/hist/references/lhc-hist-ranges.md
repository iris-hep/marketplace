# Advice on Histogram binning and Limits for LHC variables

It is difficult to do this without looking at the data first. But you need to come up with something if you've not seen the data. The following are rules of thumb:

## Binning

Choose 50 bins as a good solid starting point for each axis

## Axis Limits

The following are some guesses given we are at the LHC on the ATLAS experiment. Remember to track units!

- Jet energy and momenta: 0-300 GeV
- Eta: from -4.5 to 4.5 (unless there are cuts applied, then you can make this tighter)
- Phi: -pi to pi
- Mass: Depends on the object you are aiming for.
  - Top Quark: Mass is 173 GeV, so 0 to 250 GeV
  - Higgs: Mass is 125 so 0 to 150
  - W: Mass is 82, so 0 to 120
  - Z: Mass is 91, so 0 to 130
  - J/Psi: 0 to 10 GeV
  - Unknown: Safe between 0 and 300 GeV
- Missing ET: 0 to 200 GeV
- btagging discriminant: -5 to 15 (it is a ratio of NN outputs).
