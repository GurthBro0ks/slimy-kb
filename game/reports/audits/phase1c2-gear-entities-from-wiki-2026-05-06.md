# Phase 1C.2 Gear Entities From Wiki Audit

Generated UTC: 2026-05-06T16:16:32.292686+00:00

## Scope

Create gear entity candidates from Gear.wiki aggregate table rows.
No canonical data was modified.

## Counts

- source_text: live_api
- local_gear_wiki_lines: 975
- live_gear_wiki_lines: 975
- parsed_gearrow_templates: 422
- raw_entity_candidates: 422
- deduped_entity_candidates: 313
- entities_with_any_stat: 313
- low_confidence_entities: 0
- stat_scaling_rows: 1252
- source_facts: 313

## Entity Preview

| Name | HP | ATK | DEF | RUSH | Effect | Origin | Confidence |
|---|---:|---:|---:|---:|---|---|---:|
| Ice Skates | 0 | 20 | 0 | 0 | In [[Koryeo]], INTEL gained +1% | Exchange Kimchi Jar x5 in [[Koryeo]] | 0.85 |
| Crowbar | 0 | 20 | 0 | 0 |  | Exchange Kimchi Jar x6 in [[Koryeo]] | 0.85 |
| Royal Underwear | 0 | 0 | 20 | 0 | In [[Yamato]], INTEL gained +1% | Exchange Koban x6 in [[Yamato]] | 0.85 |
| Light Yamato Armor | 0 | 0 | 20 | 0 |  | Exchange Koban x5 in [[Yamato]] | 0.85 |
| Iron Helmet | 0 | 0 | 20 | 0 | In [[Cathay]], INTEL gained +1% | Exchange Mahjong x6 in [[Cathay]] | 0.85 |
| Podao | 0 | 20 | 0 | 0 |  | Exchange Mahjong x5 in [[Cathay]] | 0.85 |
| Tactical Boots | 0 | 0 | 0 | 20 | In [[Murika]], INTEL gained +1% | Exchange Bullet x6 in [[Murika]] | 0.85 |
| Smoothbore | 0 | 20 | 0 | 0 |  | Exchange Bullet x5 in [[Murika]] | 0.85 |
| Gentleman's Staff | 0 | 0 | 20 | 0 | In [[Britland]], INTEL gained +1% | Exchange Anchor x6 in [[Britland]] | 0.85 |
| Top Hat | 0 | 20 | 0 | 0 |  | Exchange Anchor x5 in [[Britland]] | 0.85 |
| Linen Robe | 0 | 20 | 0 | 0 | in [[Kemet]], INTEL gained +1% | Exchange Ankh x6 in [[Kemet]] | 0.85 |
| Khopesh | 0 | 20 | 0 | 0 |  | Exchange Ankh x5 in [[Kemet]] | 0.85 |
| Bronze Helmet | 0 | 0 | 20 | 0 | in [[Hellas]], INTEL gained +1% | Exchange Feather x6 in [[Hellas]] | 0.85 |
| Javelin | 0 | 20 | 0 | 0 |  | Exchange Feather x5 in [[Hellas]] | 0.85 |
| Sikh Turban | 0 | 0 | 20 | 0 | in [[Bharata]], INTEL gained +1% | Exchange Rosary x6 in [[Bharata]] | 0.85 |
| Twin Tip Dagger | 0 | 20 | 0 | 0 |  | Exchange Feather x5 in [[Hellas]] | 0.85 |
| Broken Second Hand | 0 | 20 | 0 | 0 |  | Exchange {{RewardIconWithText|Time Frag Card Gray | 0.85 |
| Broken Minute Hand | 0 | 0 | 20 | 0 |  | Exchange {{RewardIconWithText|Time Frag Card Gray | 0.85 |
| Broken Hour Hand | 0 | 0 | 0 | 20 |  | Exchange {{RewardIconWithText|Time Frag Card Gray | 0.85 |
| Parsian Pike | 0 | 0 | 0 | 20 |  | Exchange x5 in [[Parsia]] | 0.85 |
| Parsian Kite Shield | 0 | 0 | 20 | 0 | Parsian Exploration, INTEL +1% | Exchange x6 in [[Parsia]] | 0.85 |
| Motorbike Helmet | 300 | 0 | 10 | 0 | In [[Koryeo]], DMG +2% | Exchange {{retext|Kimchi Jar|green | 0.85 |
| Switchblade | 0 | 30 | 0 | 10 | In [[Koryeo]], INTEL gained +2% | Ice Skates + Crowbar | 0.85 |
| Ninjutsu Armband | 0 | 30 | 0 | 10 | In [[Yamato]], DMG +2% | Exchange {{retext|Koban|green | 0.85 |
| Golden Yamato Armor | 300 | 0 | 10 | 0 | In [[Yamato]], INTEL gained +2% | Light Yamato Armo + Royal Underwear | 0.85 |
| Heart-Protection Mirror | 300 | 0 | 10 | 0 | In [[Cathay]], DMG +2% | Exchange {{retext|Mahjong|green | 0.85 |
| Wu Scimitar | 0 | 30 | 0 | 10 | In [[Cathay]], INTEL gained +2% | Iron Helmet + Podao | 0.85 |
| Tactical Vest | 300 | 0 | 10 | 0 | In [[Murika]], DMG +2% | Exchange {{retext|Bullet|green | 0.85 |
| Colt Revolver | 0 | 30 | 0 | 10 | In [[Murika]], INTEL gained +2% | Tactical Boots + Smoothbore | 0.85 |
| Royal Guard Bearskin Hat | 300 | 0 | 10 | 0 | In [[Britland]], DMG +2% | Exchange {{retext|Anchor|green | 0.85 |
| Lee Enfield Rifle | 0 | 30 | 0 | 10 | In [[Britland]], INTEL gained +2% | Gentleman's Staff + Top Hat | 0.85 |
| Leather Shield | 300 | 0 | 10 | 0 | In [[Kemet]], DMG +2% | Exchange {{retext|Ankh|green | 0.85 |
| Poisoned Dagger | 0 | 30 | 0 | 10 | In [[Kemet]], INTEL Gained +2% | Khopesh + Linen Robe | 0.85 |
| Heavy Infantry Helmet | 300 | 0 | 10 | 0 | In [[Hellas]], INTEL gained +2%<br>Every Costume Stat +1% | Exchange {{retext|Feather|green | 0.85 |
| Legion Javelins | 0 | 30 | 0 | 10 | In [[Hellas]], INTEL gained +2%<br>Every Costume Stat +1% | Javelin + Bronze Helmet | 0.85 |
| Mughal Soldier Helmet | 300 | 0 | 10 | 0 | In [[Bharata]], DMG +2% | Exchange {{retext|Rosary|green | 0.85 |
| Pata | 0 | 30 | 0 | 10 | In [[Bharata]], INTEL gained +2% | Twin Tip Dagger + Sikh Turban | 0.85 |
| Time Hand | 0 | 30 | 0 | 10 | In the [[Time Rift | Rift]], INTEL gained +2% | 0.85 |
| Time Cog | 300 | 0 | 10 | 0 | In the [[Time Rift | Rift]], DMG +2% | 0.85 |
| Bichaq | 0 | 30 | 0 | 10 | In [[Parsia]], DMG +2% | Exchange {{Retext|Parsian Carpet|green | 0.85 |
| Pesh-Kabz | 300 | 0 | 10 | 0 | In [[Parsia]], INTEL +2% | {{RewardIconWithText|Parsian Kite Shield | 0.85 |
| Bulletproof Vest | 200 | 20 | 20 | 20 | In [[Koryeo]], DMG +2%<br>In [[Koryeo]], INTEL gained +2% | Exchange {{retext|Kimchi Jar|blue | 0.85 |
| Assault Rifle Model 98 | 100 | 30 | 10 | 30 | In [[Koryeo]], DMG +2%<br>In [[Koryeo]], INTEL gained +2% | {{retext|Motorbike Helmet|green | 0.85 |
| Servant Spirit Pendant | 200 | 20 | 20 | 20 | In [[Yamato]], DMG +2%<br>In [[Yamato]], INTEL gained +2% | Exchange {{retext|Koban|blue | 0.85 |
| Crimson Haori Jacket | 300 | 10 | 30 | 10 | In [[Yamato]], DMG +2%<br>In [[Yamato]], INTEL gained +2% | {{retext|Golden Yamato Armor|green | 0.85 |
| Rainbow Tassel | 200 | 20 | 20 | 20 | In [[Cathay]], DMG +2%<br>In [[Cathay]], INTEL gained +2% | Exchange {{retext|Mahjong|blue | 0.85 |
| Ancient Blade | 100 | 300 | 10 | 30 | In [[Cathay]], DMG +2%<br>In [[Cathay]], INTEL gained +2% | {{retext|Wu Scimitar|green | 0.85 |
| PASGT Helmet | 200 | 20 | 20 | 20 | In [[Murika]], DMG +2%<br>In [[Murika]], INTEL gained +2% | Exchange {{retext|Bullet|blue | 0.85 |
| Springfield Rifle | 100 | 30 | 10 | 30 | In [[Murika]], DMG +2%<br>In [[Murika]], INTEL gained +2% | {{retext|Colt Revolver|green | 0.85 |
| Tuxedo | 200 | 20 | 20 | 20 | In [[Britland]], DMG +2%<br>In [[Britland]], INTEL gained +2%<br>In [[Britland]] | Exchange {{retext|Anchor|blue | 0.85 |
| Sword Cane | 100 | 30 | 10 | 30 | in [[Britland]]In [[Britland]], DMG +2%<br>In [[Britland]], INTEL gained +2%<br> | {{retext|Lee Enfield Rifle|green | 0.85 |
| Tactical Helmet | 200 | 20 | 20 | 20 | In [[Kemet]], DMG +2%<br>In [[Kemet]], INTEL gained +2% | Exchange {{retext|Ankh|blue | 0.85 |
| Duckbill Axe | 100 | 30 | 10 | 30 | In [[Kemet]], DMG +2%<br>In [[Kemet]], INTEL gained +2% | {{retext|Poisoned Dagger|green | 0.85 |
| Spartan Shield | 200 | 20 | 20 | 20 | In [[Hellas]], INTEL gained +2%<br> | In [[Hellas]], DMG +2%<br>Every Costume Stat +2% | 0.85 |
| Macedonian Spear | 100 | 30 | 10 | 30 | In [[Hellas]], INTEL gained +2%<br> | In [[Hellas]], DMG +2%<br>Every Costume Stat +2% | 0.85 |
| Mahatma's Robe | 200 | 20 | 20 | 20 | In [[Bharata]], DMG +2%<br>In [[Bharata]], INTEL gained +2% | Exchange {{retext|Rosary|blue | 0.85 |
| Kukri | 100 | 30 | 10 | 30 | In [[Bharata]], DMG +2%<br>In [[Bharata]], INTEL gained +2% | {{retext|Pata|green | 0.85 |
| Time Wheel | 100 | 30 | 10 | 30 | In the [[Time Rift | Rift]], DMG +2%<br>In the [[Time Rift | 0.85 |
| Time Blade | 200 | 20 | 20 | 20 | In the [[Time Rift | Rift]], DMG +2%<br>In the [[Time Rift | 0.85 |
| War Scythes | 200 | 20 | 20 | 20 | In [[Parsia]], DMG +2%<br>In [[Parsia]], INTEL +2% | Exchange {{Retext|Parsian Carpet|blue | 0.85 |
| Shamshir | 300 | 10 | 30 | 10 | In [[Parsia]], DMG +2%<br>In [[Parsia]], INTEL +2% | {{RewardIconWithText|Pesh-Kabz|green | 0.85 |
| Pirate | 300 | 10 | 30 | 10 | Enemies in Explorations drop +20 B-tads<br>Tadpoles Gained:2,600,000 | Divine Chaos Chest (0.8% chance) | 0.85 |
| Iron Track | 100 | 10 | 10 | 50 | Travel SPD +1.6% | Divine Order Chest (0.8% chance) | 0.85 |
| Diver | 300 | 10 | 10 | 30 | In any Realm, 2x Demon God Cell Drops +2% | Divine Neutral Chest (0.8% chance) | 0.85 |
| Gas Mask | 400 | 40 | 40 | 40 | In [[Koryeo]], DMG +4%<br>In [[Koryeo]], INTEL gained +4% | Obtained from Home Chest | 0.85 |
| Golden Assault Rifle | 200 | 60 | 20 | 60 | In [[Koryeo]], DMG +4%<br>In [[Koryeo]], INTEL gained +4% | {{retext|Bulletproof Vest|blue | 0.85 |
| Genji Shield | 400 | 40 | 40 | 40 | In [[Yamato]], Snail ATK +48<br>In [[Yamato]], Snail DEF +48 | Reward of [[Yamato]] INTEL "Genji III" | 0.85 |
| Genji Helmet | 600 | 20 | 60 | 20 | In [[Yamato]], Snail DEF +48 | Reward of [[Yamato]] INTEL "Genji I" | 0.85 |
| Genji Gloves | 200 | 60 | 20 | 60 | In [[Yamato]], Snail ATK +48 | Reward of [[Yamato]] INTEL "Genji II" | 0.85 |
| Blade Muramasa | 200 | 60 | 20 | 60 | In [[Yamato]], DMG +4%<br>In [[Yamato]], INTEL gained +4% | Exchange {{retext|Koban|purple | 0.85 |
| Royal Banner | 600 | 20 | 60 | 20 | In [[Yamato]], DMG +4%<br>In [[Yamato]], INTEL gained +4% | {{retext|Crimson Haori Jacket|blue | 0.85 |
| Silver Lion | 400 | 40 | 40 | 40 | In [[Cathay]], DMG +4%<br>In [[Cathay]], INTEL gained +4% | Exchange {{retext|Mahjong|purple | 0.85 |
| 7-Star Blade | 200 | 60 | 20 | 60 | In [[Cathay]], DMG +4%<br>In [[Cathay]], INTEL gained +4% | {{retext|Ancient Blade|blue | 0.85 |
| Mechanical Exoskeleton | 400 | 40 | 40 | 40 | In [[Murika]], Snail ATK +48<br>In [[Murika]], Snail DEF +48 | Reward of [[Murika]] INTEL | 0.85 |
| Powered Glove | 200 | 60 | 20 | 60 | In [[Murika]], Snail DEF +48 | Reward of [[Murika]] INTEL | 0.85 |
| Holographic Tactical Glasses | 600 | 20 | 60 | 20 | In [[Murika]], Snail ATK +48 | Reward of [[Murika]] INTEL | 0.85 |
| Long Range Scope | 600 | 20 | 60 | 20 | In [[Murika]], DMG +4%<br>In [[Murika]], INTEL gained +4% | Exchange {{retext|Bullet|purple | 0.85 |
| M4 Carbine | 200 | 60 | 20 | 60 | In [[Murika]], DMG +4%<br>In [[Murika]], INTEL gained +4% | {{retext|Springfield Rifle|blue | 0.85 |
| Britland Crown | 400 | 40 | 40 | 40 | In [[Britland]], DMG +4%<br>In [[Britland]], INTEL gained +4%<br>In [[Britland]] | Exchange {{retext|Anchor|purple | 0.85 |
| Shotgun Umbrella | 200 | 60 | 20 | 60 | In [[Britland]], DMG +4%<br>In [[Britland]], INTEL gained +4%<br>In [[Britland]] | {{retext|Sword Cane|blue | 0.85 |

## Decision

Candidates are ready for schema-readiness validation, not canonical promotion.

## Recommended Next Step

Run Phase 1C.3 to validate candidate gear entities against gear.schema.json and produce a manual promotion packet.

