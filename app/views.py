# by Marcus Huderle, 2015

from flask import render_template, flash
from app import app
from forms import TrainerIdForm
import pymongo

import datetime
import random

uriString = app.config['MONGOSOUP_URL']
client = pymongo.MongoClient(uriString)
db = client.get_default_database()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	form = TrainerIdForm()
	if form.validate_on_submit():
		if form.trainer_id.data.isdigit():
			trainer_id = int(form.trainer_id.data)
			if trainer_id < 0 or trainer_id > 65535:
				flash('You entered an invalid Trainer ID "%s". The Trainer ID must be a number between 0-65535.' % (form.trainer_id.data))
			else:
				try:
					code = get_code(int(trainer_id))
				except:
					flash('Something went wrong. :(  Contact shantytownred@gmail.com so he can fix it!')
					return render_template("index.html", form=form)

				html = render_template("index.html", form=form, code=code)
				try:
					code = {
						'date': datetime.datetime.utcnow(),
						'trainer_id': trainer_id,
						'numbers': code,
					}
					db.codes.insert(code)
				except:
					pass
				return html
		else:
			flash('You entered an invalid Trainer ID "%s". The Trainer ID must be a number between 0-65535.' % (form.trainer_id.data))

	return render_template("index.html", form=form)

def get_code(trainer_id):
	# sunglasses squirtle
	mon_id = 0xb1 # Squirtle
	move_1 = 0x21 # Tackle
	move_2 = 0x2d # Growl
	move_3 = 0
	move_4 = 0
	spdspc_iv = random.randint(0, 255) # random DVs
	atkdef_iv = random.randint(0, 255) # random DVs
	level = 0x5
	alt_sprite = 0x10

	return gen_code(mon_id, move_1, move_2, move_3, move_4, spdspc_iv, atkdef_iv, level, alt_sprite, trainer_id)


def gen_code(mon_id, move_1, move_2, move_3, move_4, spdspc_iv, atkdef_iv, level, alt_sprite, trainer_id):
	trainer_id_hi = trainer_id >> 8
	trainer_id_lo = trainer_id & 0xff

	# xor the first four bytes with the high byte of trainer id
	new_mon_id = mon_id ^ trainer_id_hi
	new_move_1 = move_1 ^ trainer_id_hi
	new_move_2 = move_2 ^ trainer_id_hi
	new_move_3 = move_3 ^ trainer_id_hi

	# xor the next 5 bytes with the low byte of trainer id
	new_move_4     = move_4    	^ trainer_id_lo
	new_spdspc_iv  = spdspc_iv 	^ trainer_id_lo
	new_atkdef_iv  = atkdef_iv 	^ trainer_id_lo
	new_level      = level     	^ trainer_id_lo
	new_alt_sprite = alt_sprite ^ trainer_id_lo

	# generate two checksum bytes
	checksum_1 =  (new_mon_id    & 0x01) << 7
	checksum_1 += (new_move_1    & 0x02) << 5
	checksum_1 += (new_move_2    & 0x04) << 3
	checksum_1 += (new_move_3    & 0x08) << 1
	checksum_1 += (new_move_4    & 0x10) >> 1
	checksum_1 += (new_spdspc_iv & 0x20) >> 3
	checksum_1 += (new_atkdef_iv & 0x40) >> 5
	checksum_1 += (new_level     & 0x80) >> 7

	checksum_2 =  (new_alt_sprite & 0x08) << 4
	checksum_2 += (new_mon_id     & 0x10) << 2
	checksum_2 += (new_move_1     & 0x20)
	checksum_2 += (new_move_2     & 0x40) >> 2 
	checksum_2 += (new_move_3     & 0x80) >> 4
	checksum_2 += (new_move_4     & 0x01) << 2
	checksum_2 += (new_spdspc_iv  & 0x02)
	checksum_2 += (new_atkdef_iv  & 0x04) >> 2 

	checksum_3 = (new_mon_id + new_move_1 + new_move_2 + new_move_3 + new_move_4 + new_spdspc_iv \
					+ new_atkdef_iv + new_level + new_alt_sprite + trainer_id_hi) & 0xff

	checksum_4 = (new_mon_id + new_move_1 + new_move_2 + new_move_3 + new_move_4 + new_spdspc_iv \
					+ new_atkdef_iv + new_level + new_alt_sprite + trainer_id_lo) & 0xff

	return [
		new_mon_id,
		new_move_1,
		new_move_2,
		new_move_3,
		new_move_4,
		new_spdspc_iv,
		new_atkdef_iv,
		new_level,
		new_alt_sprite,
		checksum_1,
		checksum_2,
		checksum_3,
		checksum_4
	]


