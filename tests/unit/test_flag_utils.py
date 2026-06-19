"""Unit tests for flag hashing and validation utilities."""

import hashlib

import pytest

from app.flag_utils import hash_flag, validate_flag


# --- hash_flag ---


def test_hash_flag_returns_64_char_hex_string():
    result = hash_flag("CTF{my_flag}")
    assert len(result) == 64
    assert all(c in "0123456789abcdef" for c in result)


def test_hash_flag_is_deterministic():
    flag = "CTF{deterministic}"
    assert hash_flag(flag) == hash_flag(flag)


def test_hash_flag_different_inputs_produce_different_hashes():
    assert hash_flag("CTF{flag_one}") != hash_flag("CTF{flag_two}")


def test_hash_flag_empty_string_produces_known_sha256():
    expected = hashlib.sha256(b"").hexdigest()
    assert hash_flag("") == expected


# --- validate_flag ---


def test_correct_flag_is_validated_successfully():
    flag = "CTF{correct_flag}"
    stored = hash_flag(flag)
    assert validate_flag(flag, stored) is True


def test_wrong_flag_is_not_validated():
    stored = hash_flag("CTF{real_flag}")
    assert validate_flag("CTF{wrong_flag}", stored) is False


def test_validation_is_case_sensitive_uppercase_variant_fails():
    stored = hash_flag("ctf{lowercase}")
    assert validate_flag("CTF{LOWERCASE}", stored) is False


def test_validation_is_case_sensitive_lowercase_variant_fails():
    stored = hash_flag("CTF{MixedCase}")
    assert validate_flag("ctf{mixedcase}", stored) is False


def test_flag_with_leading_whitespace_fails_validation():
    stored = hash_flag("CTF{exact}")
    assert validate_flag(" CTF{exact}", stored) is False


def test_flag_with_trailing_whitespace_fails_validation():
    stored = hash_flag("CTF{exact}")
    assert validate_flag("CTF{exact} ", stored) is False


@pytest.mark.parametrize("flag", [
    "CTF{simple}",
    "CTF{with spaces inside}",
    "CTF{with_underscores_and-dashes}",
    "CTF{UPPERCASE}",
    "CTF{1234567890}",
    "CTF{special!@#$%^&*()}",
])
def test_flag_round_trip_hash_and_validate(flag):
    stored = hash_flag(flag)
    assert validate_flag(flag, stored) is True


@pytest.mark.parametrize("wrong_flag", [
    "",
    " ",
    "CTF{}",
    "no_prefix_here",
    "ctf{lowercase_prefix}",
])
def test_different_flag_always_fails_validation(wrong_flag):
    stored = hash_flag("CTF{correct}")
    assert validate_flag(wrong_flag, stored) is False
