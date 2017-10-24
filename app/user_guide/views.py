from flask import Flask, render_template, redirect, request, url_for, flash, session
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from . import user_guide
from .. import db
from ..models import User
from ..email import send_email

