def generate_block(order, prev_line, model, length):
    if prev_line:
        model.set_seed(tuple(prev_line[-order:]))
    return model.random_gen(length=(order + length))[order:]


def generate_subscore(offset, melody_sequence, model, length):
    model.set_seed(tuple(melody_sequence[:offset]))
    return model.random_gen(length=length)


def generate_block_with_pitch(order, prev_line, model, length, pitch_level, ref_avg_pitch):
    # refernce를 pitch_level 1이라 가정했을 때 목표하는 pitch_level에 맞는 멜로디가 생성될때 까지 반복
    diff = float(pitch_level - 1)
    target_avg_pitch = ref_avg_pitch + diff # 목표하는 평균 pitch

    block = generate_block(order=order, prev_line=prev_line, model=model, length=length)
    while sum(block) / float(len(block)) < target_avg_pitch :
        block = generate_block(order, prev_line, model, length)

    return block