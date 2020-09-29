melee_chain_parts = [
    ['chain_body', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['chain_legs', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['chain_boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

melee_plate_parts = [
    ['plate_body', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['plate_legs', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['plate_boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

ironman_parts = [
    ['body', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['legs', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

mage_parts = [
    ['robe_top', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['robe_bottom', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

range_parts = [
    ['body', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['chaps', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

barrows_melee = [
    ['platebody', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['platelegs', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

barrows_range = [
    ['leathertop', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['chainskirt', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

barrows_mage = [
    ['robetop', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['robeskirt', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

barrows_verac = [
    ['brassard', 'leather_chestplate.png', 'leather_chestplate_overlay.png'],
    ['plateskirt', 'leather_leggings.png', 'leather_leggings_overlay.png'],
    ['boots', 'leather_boots.png', 'leather_boots_overlay.png']
]

# Armor tints
ARMOR_DEFINITIONS = [
    # Chain armor
    ['bronze', '#604C31', melee_chain_parts],
    ['iron', '#595252', melee_chain_parts],
    ['steel', '#706666', melee_chain_parts],
    ['mithril', '#4D4D64', melee_chain_parts],
    ['adamant', '#4F7056', melee_chain_parts],
    ['rune', '#486C77', melee_chain_parts],
    ['dragon', '#6D0F09', melee_chain_parts],
    # Plate armor
    ['bronze', '#564229', melee_plate_parts],
    ['iron', '#655F5F', melee_plate_parts],
    ['steel', '#A59797', melee_plate_parts],
    ['black', '#000001', melee_plate_parts],
    ['mithril', '#45476C', melee_plate_parts],
    ['adamant', '#334B38', melee_plate_parts],
    ['rune', '#41575F', melee_plate_parts],
    ['dragon', '#440100', melee_plate_parts],
    # Mage armor
    ['blue_wizard', '#3C7EE8', mage_parts],
    ['black_wizard', '#0E0E0E', mage_parts],
    ['spider_silk', '#D7D7D7', mage_parts],
    ['batwing', '#804FB0', mage_parts],
    ['mystic', '#30ABF2', mage_parts],
    ['infinity', '#A61BB3', mage_parts],
    ['druidic', '#8EBD7E', mage_parts],
    ['dagonhai', '#524949', mage_parts],
    # Leather armor
    ['leather', '#485424', range_parts],
    ['studded_leather', '#7F7F37', range_parts],
    ['snakeskin', '#9D8E43', range_parts],
    ['green_dhide', '#13A131', range_parts],
    ['blue_dhide', '#4A50EA', range_parts],
    ['red_dhide', '#A81D0D', range_parts],
    ['black_dhide', '#0A0A0A', range_parts],
    # Ironman armor
    ['ironman', '#857C7B', ironman_parts[0:1]],  # Plate body
    ['ironman', '#928888', ironman_parts[1:]],  # Plate legs/boots
    ['ultimate_ironman', '#B9AFAE', ironman_parts[0:1]],
    ['ultimate_ironman', '#908686', ironman_parts[1:]],
    ['hardcore_ironman', '#744442', ironman_parts[0:1]],
    ['hardcore_ironman', '#6B3F3C', ironman_parts[1:]],
    # Barrows armor
    ['ahrims', '#3B3A26', barrows_mage],  # robetop robeskirt boots
    ['dharoks', '#3B3A26', barrows_melee],  # boots platebody platelegs
    ['torags', '#3B3A26', barrows_melee],  # boots platebody platelegs
    ['guthans', '#3B3A26', barrows_melee],  # boots platebody platelegs
    ['karils', '#3B3A26', barrows_range],  # leathertop chainskirt boots
    ['veracs', '#3B3A26', barrows_verac]  # brassard plateskirt boots
]