"""
Module to stream data from the KITE API via a websocket connection
"""
import logging
from kiteconnect import KiteTicker
from dotenv import load_dotenv
import threading
from token_request import get_token_from_endpoint
from utils import read_env
from write_data import processor

# Load the environment variables
load_dotenv()
# LOADING ENV VARS FROM .env
try:
    ENDPOINT = read_env("ENDPOINT")
except LookupError as err:
    raise LookupError("Did not find the following env variable") from err

logging.basicConfig(level=logging.DEBUG)

# load access token from a temp file if it exists. else, set the value to None
try:
    content = [] # empty list to store the content of the file
    with open("__TOKEN_STORE.txt", "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            content.append(line.strip())

    # Access token is stored in the first line of the file
    ACCESS_TOKEN = content[0]
    # Api key is stored in the second line of the file
    API_KEY = content[1]

except FileNotFoundError:
    ACCESS_TOKEN = None
    API_KEY = None

# Check if we've already got an access token.
if not ACCESS_TOKEN or not API_KEY:
    # We haven't writen the token and key to a file
    ACCESS_TOKEN = get_token_from_endpoint(ENDPOINT)[0] # get the access token
    API_KEY = get_token_from_endpoint(ENDPOINT)[1] # get the api key
    # Write the token and key to a file
    with open("__TOKEN_STORE.txt", "w") as f:
        f.write(ACCESS_TOKEN)
        f.write("\n")
        f.write(API_KEY)
    # Initialise Kite Connect object with access token.
    kws = KiteTicker(API_KEY, ACCESS_TOKEN)
else:
    try:
        # Initialise Kite Connect object with access token.
        kws = KiteTicker(API_KEY, ACCESS_TOKEN)
    except ValueError:
        raise ValueError("Invalid API key or Access token") from None


def on_ticks(web_socket, ticks):
    """Callback to receive ticks."""
    # logging.debug("Ticks: %s", ticks)
    data = ticks
    threading.Thread(target=processor, args=(data,)).start()

def on_connect(web_socket, response):
    """Callback on successful connect.
    Subscribe to a list of instrument_tokens (RELIANCE and ACC here)."""
     # Callback on successful connect.
    web_socket.subscribe([121345,113921,1147137,1793,4923649,1378561,3329,4724993,5633,1805569,481025,3478273,6401,3861249,5058817,5533185,7707649,8705,4617985,10241,425729,4565249,3350017,2079745,4430593,375553,20225,6483969,3495937,2995969,1148673,3456257,3020289,4524801,25601,303361,3899905,325121,4492033,42497,34817,82945,5235969,460033,724225,2941697,39425,5535489,6599681,40193,3676417,41729,2753281,4419329,4562177,49409,2332417,1376769,6422529,6247169,54273,5166593,3811585,60417,4505089,4538369,386049,2974209,3691009,1436161,67329,7685889,5436929,70401,71169,5479937,2031617,5097729,3586049,1510401,3402241,4267265,4999937,3848705,81153,4268801,78849,78081,3712257,2344449,2895105,85761,86529,87297,3553281,579329,1195009,1214721,2912513,89601,94209,94977,101121,103425,5404929,3729153,3430401,107265,3522817,548865,98049,108033,134657,981505,2714625,112129,2911489,122881,1790465,4931841,4423425,126721,2127617,6404353,97281,131329,4966657,558337,3887105,2261249,140033,5013761,382465,2029825,1591297,149249,2763265,5160961,5567745,999937,5204225,152321,7452929,320001,2931713,3905025,3812865,5420545,628225,3835393,158465,3406081,160001,3849985,7683073,160769,2187777,163073,69121,524545,5565441,175361,1316353,177665,1459457,183041,5215745,5506049,2955009,3876097,2620929,1215745,4474113,189185,189953,730625,1131777,193793,4376065,3831297,486657,1471489,4639745,4569857,4577537,197633,2067201,199937,2924289,3513601,207617,209153,3798529,211713,5105409,3851265,4536833,215553,4933377,219393,3938305,2907905,6248705,4630017,3721473,5556225,2800641,5552641,3771393,5263361,3947265,2983425,225537,2885377,2986753,1158401,5456385,714753,6244097,3885825,3870465,232961,234497,235265,3942145,3492609,237569,239873,3460353,2578945,4818433,1256193,3377153,251137,4314113,233729,5415425,244481,245249,6211841,3016193,254209,2936577,173057,4476417,258049,413185,1253889,261889,304641,3509761,6280193,958465,1586689,265729,266497,3661825,3735553,274689,7872513,7689729,4704769,299009,277761,1207553,336641,5155841,1777665,1401601,281601,3004161,3504129,6405889,2012673,4296449,70913,3047681,3045377,329985,288513,291585,403457,303617,295169,1895937,4460545,401921,3463169,4754177,1014529,3432705,302337,36865,2585345,2796801,4576001,3064577,3039233,151553,315393,5256705,316161,1753089,1020673,3471361,3518721,5425921,2971137,293121,300545,319233,324353,2259969,3520001,2713345,1332225,5051137,3378433,1124097,1609217,428033,12289,4647425,996353,2513665,3575297,1850625,340481,1086465,341249,119553,3982081,342017,592897,179457,669185,1177089,345089,1804289,6914049,5619457,734209,2475009,372481,3669505,348161,348929,3766273,589569,351233,352001,4592385,4918017,359169,359937,356865,364545,370689,526337,803329,874753,5331201,361473,3066625,655873,3606017,1270529,5573121,4774913,637185,3717889,377857,3060993,2863105,379393,380161,381697,111617,162305,3346433,3343617,3074305,1246721,389377,1215233,4940545,7712001,3699201,2745857,3663105,56321,391681,4924161,415745,2393089,3484417,519425,524289,3068673,2989313,790529,2883073,1216257,7458561,1346049,4865,4159745,3520257,408065,408833,3384577,2010113,3752193,1517057,2865921,5225729,418049,3920129,1276417,424961,1439233,428801,1442049,441857,3382017,2881537,1316609,2661633,2933761,3011329,5319169,437249,1034497,2983681,449537,774145,2876417,3149825,1723649,5284353,3397121,3453697,3036161,3695361,3908097,3491073,1134081,1149697,4574465,3041281,3001089,828673,4632577,712449,931073,7670273,3877377,462081,462849,464385,756481,5406465,4835585,3444993,469761,306177,2061825,470529,3832833,2630657,471297,3394561,3407361,3438081,475905,3425537,4849665,4896257,4259585,4870401,5359617,7398145,3912449,4307713,3871745,491265,492033,2478849,3817473,2707713,498945,3550721,6386689,4561409,4752385,3692289,506625,2939649,4923905,727297,667137,4690177,511233,147969,2968577,416513,3536897,3587585,516609,2672641,2893057,3400961,1257217,4488705,587265,533761,534529,519937,3823873,4506369,4437249,2060801,98561,6281729,3042305,4665857,4879617,3841793,539137,1041153,339969,2708225,2815745,50945,543745,5561857,548353,5728513,4471809,7399937,130305,2452737,6629633,3623425,3675137,1124865,630529,3544065,4596993,5332481,1718529,1520129,578305,1076225,3826433,1152769,2707969,582913,584449,416769,2395137,693505,3458817,590593,5088513,2666241,6054401,5200385,4892417,5228801,4427521,3696641,2877185,3031041,1003009,2832641,1629185,3564801,1027585,3756033,2702593,610561,764673,8042241,593665,3709441,2925313,3053313,3778817,611329,2538753,3944705,3612417,297985,4454401,2949633,619777,91393,3372801,2197761,3924993,625153,1933569,2977281,2762497,601601,3724033,5181953,633601,4464129,2723073,3802369,3911169,2748929,237057,7702785,760833,638209,638977,7977729,2756609,3131137,5102337,120577,648961,3689729,6519809,1038081,6500353,4385281,3530497,2994945,7455745,1347585,3650561,4701441,2905857,676609,6491649,678145,6191105,681985,7893761,2929921,617473,3563521,2236417,2402561,4518657,6583809,2455041,687873,3660545,3834113,2681089,693249,5591041,3226369,695553,5197313,5025537,4107521,701185,2259201,240641,5344513,2906881,5786113,5376257,1112065,2730497,3820033,3365633,4532225,3357697,3433985,2813441,2445313,622337,3926273,1894657,4854273,720897,1174273,2009857,2921217,5154305,3065601,4286721,728065,733697,3443457,4485121,731905,4708097,3930881,3649281,6201601,3375873,745473,738561,141569,3857409,3873025,7577089,3360257,5202689,744705,962817,4968961,7401729,32769,4281601,2078465,715265,4359425,6585345,5298689,2870273,4672513,3388417,2718209,3336961,3601409,3019265,5468673,764929,613633,767233,3598849,369153,4546049,3067649,5136129,2827521,2675969,773377,4600577,5582849,258817,7995905,669697,3659777,784897,6546945,182785,3927553,5202177,787969,1277953,2695681,26625,4911105,4544513,780289,3024129,2710529,794369,793345,3078657,3005185,3918849,1102337,806401,2828801,5504257,3608577,4834049,815617,2413569,593921,867073,3668225,1239809,3539457,3412993,940033,993281,1688577,3347457,2927361,2089729,832513,3732993,837889,3821313,5399297,779521,758529,5462785,3028225,3197185,1100545,2383105,539393,1887745,247553,850945,851713,4378881,5446401,3785729,857857,3431425,7426049,854785,558849,856321,857089,4516097,2992385,860929,864001,760321,3533057,163329,2875649,4593921,767489,3076609,6936321,866305,6192641,2622209,2394625,3818753,1018881,898305,404737,5143553,871681,185345,952577,2953217,878593,873217,414977,876289,884737,877057,895745,114433,4921089,1068033,47105,6445569,3255297,3465729,1649921,3641089,2956545,5587969,4638209,2307585,3526657,387841,387073,5485313,102145,3725313,523009,1522689,2802689,894209,889601,894977,891137,4360193,3588865,4914177,3764993,3634689,3945985,897537,900609,3529217,887297,2708481,502785,6921473,2479361,3348737,6549505,2910465,907777,79873,2886401,3637249,2170625,3646721,2873089,269569,4369665,3898369,2952193,916225,2752769,2891009,4278529,51457,2674433,923393,2889473,2263041,134913,3932673,3780097,5168129,6194177,2909185,3415553,3044353,6929153,530689,987393,4843777,784129,961793,941057,3465217,4445185,945665,947969,1080577,3507713,7496705,3677697,3475713,951809,2226177,953345,6218753,4330241,3026177,2976257,2880769,1084161,972545,964097,4610817,969473,1921537,768513,2996481,3050241,975873,1922049,275457,7436801,4514561])
     #Set subscribed equities to tick in `full` mode.
    web_socket.set_mode(web_socket.MODE_FULL, [121345,113921,1147137,1793,4923649,1378561,3329,4724993,5633,1805569,481025,3478273,6401,3861249,5058817,5533185,7707649,8705,4617985,10241,425729,4565249,3350017,2079745,4430593,375553,20225,6483969,3495937,2995969,1148673,3456257,3020289,4524801,25601,303361,3899905,325121,4492033,42497,34817,82945,5235969,460033,724225,2941697,39425,5535489,6599681,40193,3676417,41729,2753281,4419329,4562177,49409,2332417,1376769,6422529,6247169,54273,5166593,3811585,60417,4505089,4538369,386049,2974209,3691009,1436161,67329,7685889,5436929,70401,71169,5479937,2031617,5097729,3586049,1510401,3402241,4267265,4999937,3848705,81153,4268801,78849,78081,3712257,2344449,2895105,85761,86529,87297,3553281,579329,1195009,1214721,2912513,89601,94209,94977,101121,103425,5404929,3729153,3430401,107265,3522817,548865,98049,108033,134657,981505,2714625,112129,2911489,122881,1790465,4931841,4423425,126721,2127617,6404353,97281,131329,4966657,558337,3887105,2261249,140033,5013761,382465,2029825,1591297,149249,2763265,5160961,5567745,999937,5204225,152321,7452929,320001,2931713,3905025,3812865,5420545,628225,3835393,158465,3406081,160001,3849985,7683073,160769,2187777,163073,69121,524545,5565441,175361,1316353,177665,1459457,183041,5215745,5506049,2955009,3876097,2620929,1215745,4474113,189185,189953,730625,1131777,193793,4376065,3831297,486657,1471489,4639745,4569857,4577537,197633,2067201,199937,2924289,3513601,207617,209153,3798529,211713,5105409,3851265,4536833,215553,4933377,219393,3938305,2907905,6248705,4630017,3721473,5556225,2800641,5552641,3771393,5263361,3947265,2983425,225537,2885377,2986753,1158401,5456385,714753,6244097,3885825,3870465,232961,234497,235265,3942145,3492609,237569,239873,3460353,2578945,4818433,1256193,3377153,251137,4314113,233729,5415425,244481,245249,6211841,3016193,254209,2936577,173057,4476417,258049,413185,1253889,261889,304641,3509761,6280193,958465,1586689,265729,266497,3661825,3735553,274689,7872513,7689729,4704769,299009,277761,1207553,336641,5155841,1777665,1401601,281601,3004161,3504129,6405889,2012673,4296449,70913,3047681,3045377,329985,288513,291585,403457,303617,295169,1895937,4460545,401921,3463169,4754177,1014529,3432705,302337,36865,2585345,2796801,4576001,3064577,3039233,151553,315393,5256705,316161,1753089,1020673,3471361,3518721,5425921,2971137,293121,300545,319233,324353,2259969,3520001,2713345,1332225,5051137,3378433,1124097,1609217,428033,12289,4647425,996353,2513665,3575297,1850625,340481,1086465,341249,119553,3982081,342017,592897,179457,669185,1177089,345089,1804289,6914049,5619457,734209,2475009,372481,3669505,348161,348929,3766273,589569,351233,352001,4592385,4918017,359169,359937,356865,364545,370689,526337,803329,874753,5331201,361473,3066625,655873,3606017,1270529,5573121,4774913,637185,3717889,377857,3060993,2863105,379393,380161,381697,111617,162305,3346433,3343617,3074305,1246721,389377,1215233,4940545,7712001,3699201,2745857,3663105,56321,391681,4924161,415745,2393089,3484417,519425,524289,3068673,2989313,790529,2883073,1216257,7458561,1346049,4865,4159745,3520257,408065,408833,3384577,2010113,3752193,1517057,2865921,5225729,418049,3920129,1276417,424961,1439233,428801,1442049,441857,3382017,2881537,1316609,2661633,2933761,3011329,5319169,437249,1034497,2983681,449537,774145,2876417,3149825,1723649,5284353,3397121,3453697,3036161,3695361,3908097,3491073,1134081,1149697,4574465,3041281,3001089,828673,4632577,712449,931073,7670273,3877377,462081,462849,464385,756481,5406465,4835585,3444993,469761,306177,2061825,470529,3832833,2630657,471297,3394561,3407361,3438081,475905,3425537,4849665,4896257,4259585,4870401,5359617,7398145,3912449,4307713,3871745,491265,492033,2478849,3817473,2707713,498945,3550721,6386689,4561409,4752385,3692289,506625,2939649,4923905,727297,667137,4690177,511233,147969,2968577,416513,3536897,3587585,516609,2672641,2893057,3400961,1257217,4488705,587265,533761,534529,519937,3823873,4506369,4437249,2060801,98561,6281729,3042305,4665857,4879617,3841793,539137,1041153,339969,2708225,2815745,50945,543745,5561857,548353,5728513,4471809,7399937,130305,2452737,6629633,3623425,3675137,1124865,630529,3544065,4596993,5332481,1718529,1520129,578305,1076225,3826433,1152769,2707969,582913,584449,416769,2395137,693505,3458817,590593,5088513,2666241,6054401,5200385,4892417,5228801,4427521,3696641,2877185,3031041,1003009,2832641,1629185,3564801,1027585,3756033,2702593,610561,764673,8042241,593665,3709441,2925313,3053313,3778817,611329,2538753,3944705,3612417,297985,4454401,2949633,619777,91393,3372801,2197761,3924993,625153,1933569,2977281,2762497,601601,3724033,5181953,633601,4464129,2723073,3802369,3911169,2748929,237057,7702785,760833,638209,638977,7977729,2756609,3131137,5102337,120577,648961,3689729,6519809,1038081,6500353,4385281,3530497,2994945,7455745,1347585,3650561,4701441,2905857,676609,6491649,678145,6191105,681985,7893761,2929921,617473,3563521,2236417,2402561,4518657,6583809,2455041,687873,3660545,3834113,2681089,693249,5591041,3226369,695553,5197313,5025537,4107521,701185,2259201,240641,5344513,2906881,5786113,5376257,1112065,2730497,3820033,3365633,4532225,3357697,3433985,2813441,2445313,622337,3926273,1894657,4854273,720897,1174273,2009857,2921217,5154305,3065601,4286721,728065,733697,3443457,4485121,731905,4708097,3930881,3649281,6201601,3375873,745473,738561,141569,3857409,3873025,7577089,3360257,5202689,744705,962817,4968961,7401729,32769,4281601,2078465,715265,4359425,6585345,5298689,2870273,4672513,3388417,2718209,3336961,3601409,3019265,5468673,764929,613633,767233,3598849,369153,4546049,3067649,5136129,2827521,2675969,773377,4600577,5582849,258817,7995905,669697,3659777,784897,6546945,182785,3927553,5202177,787969,1277953,2695681,26625,4911105,4544513,780289,3024129,2710529,794369,793345,3078657,3005185,3918849,1102337,806401,2828801,5504257,3608577,4834049,815617,2413569,593921,867073,3668225,1239809,3539457,3412993,940033,993281,1688577,3347457,2927361,2089729,832513,3732993,837889,3821313,5399297,779521,758529,5462785,3028225,3197185,1100545,2383105,539393,1887745,247553,850945,851713,4378881,5446401,3785729,857857,3431425,7426049,854785,558849,856321,857089,4516097,2992385,860929,864001,760321,3533057,163329,2875649,4593921,767489,3076609,6936321,866305,6192641,2622209,2394625,3818753,1018881,898305,404737,5143553,871681,185345,952577,2953217,878593,873217,414977,876289,884737,877057,895745,114433,4921089,1068033,47105,6445569,3255297,3465729,1649921,3641089,2956545,5587969,4638209,2307585,3526657,387841,387073,5485313,102145,3725313,523009,1522689,2802689,894209,889601,894977,891137,4360193,3588865,4914177,3764993,3634689,3945985,897537,900609,3529217,887297,2708481,502785,6921473,2479361,3348737,6549505,2910465,907777,79873,2886401,3637249,2170625,3646721,2873089,269569,4369665,3898369,2952193,916225,2752769,2891009,4278529,51457,2674433,923393,2889473,2263041,134913,3932673,3780097,5168129,6194177,2909185,3415553,3044353,6929153,530689,987393,4843777,784129,961793,941057,3465217,4445185,945665,947969,1080577,3507713,7496705,3677697,3475713,951809,2226177,953345,6218753,4330241,3026177,2976257,2880769,1084161,972545,964097,4610817,969473,1921537,768513,2996481,3050241,975873,1922049,275457,7436801,4514561])

def on_close(web_socket, code, reason):
    """On connection close stop the main loop
    Reconnection will not happen after executing `ws.stop()`"""
    web_socket.stop()

# Assign the callbacks.
kws.on_ticks = on_ticks
kws.on_connect = on_connect
kws.on_close = on_close

# Infinite loop on the main thread. Nothing after this will run.
# You have to use the pre-defined callbacks to manage subscriptions.
kws.connect()
