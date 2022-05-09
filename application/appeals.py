from app import app, db # Точка входа в приложение Flask
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from models import Address, House, Counter, Pokaz
from forms import SetPokazForm
from application.pokaz_utils import clear_exists_pkz
from utils import cur_year, get_period, month_name