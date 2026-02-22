"""Tests for Flask routes (smoke tests)."""
import pytest


def test_index(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data


def test_contacts_list(client):
    resp = client.get("/contacts/")
    assert resp.status_code == 200


def test_donations_list(client):
    resp = client.get("/donations/")
    assert resp.status_code == 200


def test_templates_list(client):
    resp = client.get("/templates/")
    assert resp.status_code == 200


def test_send_index(client):
    resp = client.get("/send/")
    assert resp.status_code == 200


def test_email_logs(client):
    resp = client.get("/send/logs")
    assert resp.status_code == 200
