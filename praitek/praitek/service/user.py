#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from praitek.infra.account import Account as Account_infra


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def user_login(self):
        account = Account_infra()
        info = account.get_info_by_name(self.username)
        if info.disabled == 1:
            return False, 0
        elif info.password == self.password:
            return True, info.id
        else:
            return False, 0
