import pytest
from app.entities.doctor_subs import DoctorSubs


@pytest.mark.parametrize("count, expected", [
    (9999999, "10,0м"),  # более 10 миллионов (пример)
    (1_500_000, "1,5м"),  # полтора миллиона
    (999_999, "999к"),  # чуть меньше миллиона
    (100_000, "100к"),  # ровно 100 тысяч
    (150_000, "150к"),  # 150 тысяч
    (99_999, "99 999"),  # чуть меньше 10000 — тут нужно проверить
    (10_000, "10 000"),  # ровно 10 тысяч
    (15_300, "15 300"),  # 15 300
    (9_999, "9999"),  # менее 10 тысяч
])
def test_subs_short(count, expected):
    doctor = DoctorSubs(
        internal_id=1,
        doctor_id=1,
        inst_subs_count=100,
        instagram_channel_name="test",
        tg_subs_count=count,
        telegram_channel_name="test",
    )
    result = doctor.subs_short(count)
    assert result == expected


@pytest.mark.parametrize("count, expected", [
    (1, "подписчик"),
    (2, "подписчика"),
    (3, "подписчика"),
    (4, "подписчика"),
    (5, "подписчиков"),
    (11, "подписчиков"),
    (12, "подписчиков"),
    (13, "подписчиков"),
    (14, "подписчиков"),
    (15, "подписчиков"),
    (21, "подписчик"),
    (22, "подписчика"),
    (23, "подписчика"),
    (24, "подписчика"),
    (25, "подписчиков"),
    (111, "подписчиков"),
    (112, "подписчиков"),
    (113, "подписчиков"),
    (114, "подписчиков"),
    (115, "подписчиков"),
])
def test_subs_text(count, expected):
    doctor = DoctorSubs(
        internal_id=1,
        doctor_id=1,
        inst_subs_count=100,
        instagram_channel_name="test",
        tg_subs_count=count,
        telegram_channel_name="test",
    )
    text = doctor.subs_text(count)
    assert text == expected
