import streamlit as st

class _SessionState:
    def __init__(self, **kwargs):
        for key, val in kwargs.items():
            setattr(self, key, val)

def get(**kwargs):
    if not hasattr(st, '_session_state'):
        st._session_state = _SessionState(**kwargs)
    if not hasattr(st._session_state, 'page_index'):
        setattr(st._session_state, 'page_index', 0)  # or any default value
    if not hasattr(st._session_state, 'speech_speaker'):
        setattr(st._session_state, 'speech_speaker', None)  # or some other initial value
    if not hasattr(st._session_state, 'speech_date'):
        setattr(st._session_state, 'speech_date', None)  # or some other initial value
    if not hasattr(st._session_state, 'speech_description'):
        setattr(st._session_state, 'speech_description', None)  # or some other initial value
    return st._session_state