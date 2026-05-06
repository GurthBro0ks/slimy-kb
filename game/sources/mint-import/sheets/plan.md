# SuperSnail Calcs.xlsx — Full Audit Plan

## Objective
Extract and separate every tab from the Excel file, analyze all formulas, audit for errors, map cross-tab dependencies, and provide optimization recommendations.

## File Overview
- **File**: `Updated Copy of SuperSnail Calcs.xlsx`
- **Sheets**: 33 tabs total (Offering Speed, Travel Speed, Gene Research, Cells Gained, Museum, Rocket Cabin Effects, Minion Boosts, Leadership, Tadpole Pond, Fungus Farm, Time Machine, Lumber Camp, Quarry, Quantum Amp, Compass, Cost Reductions, Lottery, Minion Base Stats, Partner Research Costs, DNA Costs, Dragon DNA Costs, Relic Albums, Lotto2 Expanded Stock, Lotto3 Expanded Stock, Useful Awakenings, Rift Anecdotes, Dance Calculator, Band Calculator, Sailing Calculator, Drifter Stats, Drifter Priority, Protomon, Hitmen)
- **Total Formulas**: ~4,324+
- **Cross-sheet References**: Present in Dance Calculator, Band Calculator, Sailing Calculator
- **Sheets with No Formulas**: Lotto2 Expanded Stock, Lotto3 Expanded Stock, Useful Awakenings, Drifter Priority

## Stage 1: Extraction & Inventory (Python)
- Extract each of the 33 sheets to its own .xlsx file in `/mnt/agents/output/sheets/`
- Dump complete formula inventory per sheet (cell, formula, data type)
- Extract all unique formulas for deduplication analysis

## Stage 2: Deep Analysis (Python + Subagents)
For each sheet:
- **Formula Catalog**: Cell address, exact formula, plain-English summary, dependencies
- **Error Audit**: Check for #REF!, #N/A, #VALUE!, #DIV/0!, circular refs, suspicious hardcoded values
- **Cross-tab mapping**: Identify all inter-sheet references and build dependency graph
- **Optimization recommendations**: Nested IFs → IFS/SWITCH/XLOOKUP, redundant SUMs, volatile functions, etc.

## Stage 3: Report Generation (Subagents)
- Compile findings into a comprehensive Markdown report
- Include:
  - Executive summary
  - Per-sheet formula catalogs
  - Error audit findings
  - Cross-tab dependency matrix
  - Optimization recommendations
- Convert to .docx using the docx skill

## Stage 4: Quality Check
- Verify all 33 sheets were extracted
- Verify all formulas were captured
- Verify cross-tab references are complete
