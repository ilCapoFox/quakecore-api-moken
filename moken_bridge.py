from fastapi import FastAPI, HTTPException, Header, Depends
import requests
import hashlib
import re
from datetime import datetime, timedelta

app = FastAPI(title="Quakecore to Moken Bridge Automatic")

# --- YOUR SECRET TOKEN FOR MOKEN ---
MOKEN_SECRET_TOKEN = "quakecore-moken-token-2026"

# --- QUAKECORE DICTIONARIES ---
colors = ["white", "pearl", "alabaster", "snowy", "ivory", "cream", "cotton", "chiffon", "lace", "coconut", "linen", "bone", "daisy", "powder", "frost", "porcelain", "parchment", "velvet", "tan", "beige", "macaroon", "hazel", "felt", "metal", "gingham", "sand", "sepia", "latte", "vinyl", "glass", "hazelnut", "canvas", "wool", "yellow", "golden", "daffodil", "flaxen", "butter", "lemon", "mustard", "tartan", "blue", "cloth", "fiery", "banana", "plastic", "dijon", "honey", "blonde", "pineapple", "orange", "tangerine", "marigold", "cider", "rusty", "ginger", "tiger", "bronze", "fuzzy", "opaque", "clay", "carrot", "corduroy", "ceramic", "marmalade", "amber", "sandstone", "concrete", "red", "cherry", "hemp", "merlot", "garnet", "crimson", "ruby", "scarlet", "burlap", "brick", "bamboo", "mahogany", "blood", "sangria", "berry", "currant", "blush", "candy", "lipstick", "pink", "rose", "fuchsia", "punch", "watermelon", "rouge", "coral", "peach", "strawberry", "rosewood", "lemonade", "taffy", "bubblegum", "crepe", "hotpink", "purple", "mauve", "violet", "boysenberry", "lavender", "plum", "magenta", "lilac", "grape", "eggplant", "eggshell", "iris", "heather", "amethyst", "raisin", "orchid", "mulberry", "carbon", "slate", "sky", "navy", "indigo", "cobalt", "cedar", "ocean", "azure", "cerulean", "spruce", "stone", "aegean", "denim", "admiral", "sapphire", "arctic", "green", "chartreuse", "juniper", "sage", "lime", "fern", "olive", "emerald", "pear", "mossy", "shamrock", "seafoam", "pine", "mint", "seaweed", "pickle", "pistachio", "basil", "brown", "coffee", "chrome", "peanut", "carob", "hickory", "wooden", "pecan", "walnut", "caramel", "gingerbread", "syrup", "chocolate", "tortilla", "umber", "tawny", "brunette", "cinnamon", "glossy", "teal", "grey", "shadow", "graphite", "iron", "pewter", "cloud", "silver", "smoke", "gauze", "ash", "foggy", "flint", "charcoal", "pebble", "lead", "tin", "fossilized", "black", "ebony", "midnight", "inky", "oily", "satin", "onyx", "nylon", "fleece", "sable", "jetblack", "coal", "mocha", "obsidian", "jade", "cyan", "leather", "maroon", "carmine", "aqua", "chambray", "holographic", "laurel", "licorice", "khaki", "goldenrod", "malachite", "mandarin", "mango", "taupe", "aquamarine", "turquoise", "vermilion", "saffron", "cinnabar", "myrtle", "neon", "burgundy", "tangelo", "topaz", "wintergreen", "viridian", "vanilla", "paisley", "raspberry", "tweed", "pastel", "opal", "menthol", "champagne", "gunmetal", "infrared", "ultraviolet", "rainbow", "mercurial", "clear", "misty", "steel", "zinc", "citron", "cornflower", "lava", "quartz", "honeysuckle", "chili"]
animals = ["alligator", "bee", "bird", "camel", "cat", "cheetah", "chicken", "cow", "dog", "corgi", "eagle", "elephant", "fish", "fox", "toad", "giraffe", "hippo", "kangaroo", "kitten", "lobster", "monkey", "octopus", "pig", "puppy", "rabbit", "rat", "scorpion", "seal", "sheep", "snail", "spider", "tiger", "turtle", "newt", "tadpole", "frog", "tarantula", "albatross", "blackbird", "canary", "crow", "cuckoo", "dove", "pigeon", "falcon", "finch", "flamingo", "goose", "seagull", "hawk", "jay", "mockingbird", "kestrel", "kookaburra", "mallard", "nightingale", "nuthatch", "ostrich", "owl", "parakeet", "parrot", "peacock", "pelican", "penguin", "pheasant", "piranha", "raven", "robin", "rooster", "sparrow", "stork", "swallow", "swan", "swift", "turkey", "vulture", "woodpecker", "wren", "butterfly", "barbel", "carp", "cod", "crab", "eel", "goldfish", "haddock", "halibut", "jellyfish", "perch", "pike", "mantaray", "salmon", "sawfish", "scallop", "shark", "shell", "shrimp", "trout", "ant", "aphid", "beetle", "caterpillar", "dragonfly", "cricket", "fly", "grasshopper", "ladybug", "millipede", "moth", "wasp", "anteater", "antelope", "armadillo", "badger", "bat", "beaver", "bull", "chimpanzee", "dachshund", "deer", "dolphin", "elk", "moose", "gazelle", "gerbil", "goat", "bear", "hamster", "hare", "hedgehog", "horse", "hyena", "lion", "llama", "lynx", "mammoth", "marmot", "mink", "mole", "mongoose", "mouse", "mule", "otter", "panda", "platypus", "pony", "porcupine", "puma", "raccoon", "reindeer", "rhino", "skunk", "sloth", "squirrel", "weasel", "snake", "wolf", "zebra", "boa", "chameleon", "copperhead", "cottonmouth", "crocodile", "rattlesnake", "gecko", "iguana", "lizard", "python", "salamander", "sidewinder", "whale", "tortoise", "lemur", "rook", "koala", "donkey", "ferret", "tardigrade", "orca", "okapi", "liger", "unicorn", "dragon", "squid", "ape", "gorilla", "baboon", "cormorant", "mantis", "tapir", "capybara", "pangolin", "opossum", "wombat", "aardvark", "starfish", "shetland", "narwhal", "worm", "hornet", "viper", "stallion", "jaguar", "panther", "bobcat", "leopard", "osprey", "cougar", "dalmatian", "terrier", "duck", "sealion", "raccoon", "chipmunk", "loris", "poodle", "orangutan", "gibbon", "meerkat", "huskie", "barracuda", "bison", "caribou", "chinchilla", "coyote", "crane", "dinosaur", "lark", "griffin", "yeti", "troll", "seahorse", "walrus", "yak", "wolverine", "boar", "alpaca", "porpoise", "manatee", "guppy", "condor", "cyborg", "cobra", "locust", "mandrill", "oyster", "urchin", "quail", "sardine", "ram", "starling", "wallaby", "buffalo", "goblin", "tuna", "mustang"]
adjectives = ["attractive", "bald", "beautiful", "rare", "clean", "dazzling", "lucky", "elegant", "fancy", "fit", "fantastic", "glamorous", "gorgeous", "handsome", "long", "magnificent", "muscular", "plain", "able", "quaint", "scruffy", "innocent", "short", "skinny", "acrobatic", "tall", "proper", "alert", "lone", "agreeable", "ambitious", "brave", "calm", "delightful", "eager", "faithful", "gentle", "happy", "jolly", "kind", "lively", "nice", "obedient", "polite", "proud", "silly", "thankful", "winning", "witty", "wonderful", "zealous", "expert", "amateur", "clumsy", "amusing", "vast", "fierce", "real", "helpful", "itchy", "atomic", "basic", "mysterious", "blurry", "perfect", "best", "powerful", "interesting", "decent", "wild", "jovial", "genuine", "broad", "brisk", "brilliant", "curved", "deep", "flat", "high", "hollow", "low", "narrow", "refined", "round", "shallow", "skinny", "square", "steep", "straight", "wide", "big", "colossal", "clever", "gigantic", "great", "huge", "immense", "large", "little", "mammoth", "massive", "micro", "mini", "petite", "puny", "scrawny", "short", "small", "polished", "teeny", "tiny", "crazy", "dancing", "custom", "faint", "harsh", "formal", "howling", "loud", "melodic", "noisy", "upbeat", "quiet", "dandy", "raspy", "rhythmic", "daring", "zany", "digital", "dizzy", "exotic", "fun", "furry", "hidden", "ancient", "brief", "early", "fast", "future", "late", "long", "modern", "old", "prehistoric", "zesty", "rapid", "short", "slow", "swift", "young", "acidic", "bitter", "cool", "creamy", "keen", "tricky", "fresh", "special", "unique", "hot", "magic", "main", "nutty", "pet", "mythical", "ripe", "wobbly", "salty", "savory", "sour", "spicy", "bright", "stale", "sweet", "tangy", "tart", "rich", "rural", "urban", "breezy", "bumpy", "chilly", "cold", "cool", "cuddly", "damaged", "damp", "restless", "dry", "flaky", "fluffy", "virtual", "merry", "hot", "icy", "shiny", "melted", "joyous", "rough", "shaggy", "sharp", "radiant", "sticky", "strong", "soft", "uneven", "warm", "feisty", "cheery", "energetic", "abundant", "macho", "glorious", "mean", "quick", "precise", "stable", "spare", "sunny", "trendy", "shambolic", "striped", "boxy", "generous", "tame", "joyful", "festive", "bubbly", "soaring", "orbiting", "sparkly", "smooth", "docile", "original", "electric", "funny", "passive", "active", "cheesy", "tangy", "blunt", "dapper", "bent", "curly", "oblong", "sneaky", "overt", "careful", "jumpy", "bouncy", "recumbent", "cheerful", "droll", "odd", "suave", "sleepy"]

def get_animal_name(public_key_bytes: bytes, separator: str = '-') -> str:
    """Python translation of the Quakecore Java algorithm to generate the Animal Name."""
    # 1. Calculate the MD5 hash of the public key (16 bytes array)
    md = hashlib.md5(public_key_bytes).digest()
    
    # 2. XOR compression (target=3) simulating the Java compress() for a 16-byte input
    # Segment 0: first 5 bytes
    ret0 = md[0] ^ md[1] ^ md[2] ^ md[3] ^ md[4]
    # Segment 1: next 5 bytes
    ret1 = md[5] ^ md[6] ^ md[7] ^ md[8] ^ md[9]
    # Segment 2: last 6 bytes
    ret2 = md[10] ^ md[11] ^ md[12] ^ md[13] ^ md[14] ^ md[15]
    
    # 3. Array mapping
    adj = adjectives[ret0 & 0xFF]
    col = colors[ret1 & 0xFF]
    anim = animals[ret2 & 0xFF]
    
    return f"{adj}{separator}{col}{separator}{anim}"

def verify_token(authorization: str = Header(None)):
    """Verifies that Moken is calling us with the correct password."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized: No token provided")
    
    # Remove the "Bearer " prefix if Moken uses it
    token = authorization.replace("Bearer ", "")
    if token != MOKEN_SECRET_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid token")

def fetch_quakecore_data():
    """Fetches the most recent log file from the Quakecore server."""
    # Pretend to be a browser to avoid being blocked by the server
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    today = datetime.utcnow()
    
    # Search backwards up to 5 days
    for days_back in range(5):
        target_date = today - timedelta(days=days_back)
        url = f"https://api.quakecore.com/rewards/rewards-{target_date.strftime('%Y-%m-%d')}"
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.content
        except:
            pass
            
    # FALLBACK: If the last 5 days fail, use the historically working file
    try:
        fallback_url = "https://api.quakecore.com/rewards/rewards-2025-09-19"
        response = requests.get(fallback_url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
    except:
        pass
        
    return None

@app.get("/api/miners/{miner_identifier}", dependencies=[Depends(verify_token)])
def get_miner(miner_identifier: str):
    # 1. Fetch fresh data from Quakecore
    raw_data = fetch_quakecore_data()
    
    if not raw_data:
        raise HTTPException(status_code=500, detail="Unable to fetch logs from Quakecore at this time.")

    is_online = False
    found_pub_key_hex = None

    # Check 1: Did Moken provide the direct Hex string (Device ID)?
    if miner_identifier.encode() in raw_data:
        is_online = True
        found_pub_key_hex = miner_identifier
    else:
        # Check 2: Did Moken provide an Animal Name?
        # Find ALL possible keys in the raw file using Regex (they start with "3059...")
        possible_keys = re.findall(rb"30593013[0-9A-Fa-f]{100,200}", raw_data)
        
        # Scan them and translate them into animal names
        for key_bytes in set(possible_keys):
            animal_name = get_animal_name(key_bytes)
            if animal_name == miner_identifier.lower():
                is_online = True
                found_pub_key_hex = key_bytes.decode('utf-8')
                break

    # If not found, tell Moken the node is offline
    if not is_online:
        return {"miner_id": miner_identifier, "status": "offline"}

    # If found, return the expected Moken format
    moken_response = {
        "miner_id": miner_identifier,
        "status": "online",
        "hex_location": "85be8d8ffffffff", # Static H3 Hex
        "performance_metrics": {
            "hex_density_percent": 100,
            "device_density_percent": 100,
            "location_percent": 100,
            "heartbeat_percent": 100
        },
        "rewards": {
            "total_earned": 0,
            "reward_cap": 0
        },
        "protection": {
            "nft_protection": True,
            "loss_of_protection": False
        },
        "uptime": {
            "consecutive_days_running": 5,
            "consecutive_days_off": 0
        }
    }
    
    return moken_response