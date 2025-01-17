from datetime import datetime

words = [
    'dog', 'cat', 'house', 'car', 'book', 'tree', 'phone', 'bird', 'desk', 'lamp',
    'chair', 'bed', 'door', 'wall', 'floor', 'roof', 'clock', 'cup', 'plate', 'fork',
    'spoon', 'knife', 'bowl', 'pan', 'pot', 'oven', 'sink', 'soap', 'towel', 'brush',
    'mirror', 'shelf', 'box', 'bag', 'key', 'lock', 'coin', 'cash', 'card', 'ring',
    'watch', 'hat', 'coat', 'shoe', 'sock', 'belt', 'dress', 'shirt', 'pants', 'scarf',
    'glove', 'boots', 'sun', 'moon', 'star', 'cloud', 'rain', 'snow', 'wind', 'storm',
    'beach', 'sand', 'sea', 'lake', 'river', 'rock', 'stone', 'hill', 'park', 'grass',
    'leaf', 'flower', 'plant', 'apple', 'pear', 'plum', 'grape', 'bread', 'cake', 'pie',
    'egg', 'milk', 'juice', 'water', 'tea', 'salt', 'sugar', 'rice', 'corn', 'bean', 
    'nut', 'soup', 'ice', 'candy', 'honey', 'jam', 'oil', 'sauce', 'paper', 'pen', 'tape',
    'glue', 'pin', 'clip', 'wire', 'rope', 'yarn', 'wood', 'metal', 'glass', 'gold', 
    'steel', 'iron', 'brick', 'tile', 'paint', 'ink', 'map', 'page', 'note', 'card', 
    'gift', 'toy', 'ball', 'kite', 'game', 'puzzle', 'fence', 'gate', 'pool', 'yard', 
    'road', 'path', 'step', 'bridge', 'rail', 'train', 'bus', 'bike', 'plane', 'ship', 
    'boat', 'mall', 'shop', 'store', 'bank', 'gym', 'zoo', 'farm', 'barn'
]


def get_today_word():
    day_of_year = datetime.now().timetuple().tm_yday
    return words[day_of_year % len(words)]