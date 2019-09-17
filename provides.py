# Copyright 2019 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from charms import reactive


class MySQLSharedProvides(reactive.Endpoint):

    @property
    def database(self):
        return self.all_joined_units.received['database']

    @property
    def username(self):
        return self.all_joined_units.received['username']

    @property
    def hostname(self):
        return self.all_joined_units.received['hostname']

    def available(self):
        #TODO Rework
        for unit in self.all_joined_units:
            if not unit.received['database']:
                return False
            if not unit.received['username']:
                return False
            if not unit.received['hostname']:
                return False
        return True

    @reactive.when('endpoint.{endpoint_name}.joined')
    def joined(self):
        reactive.clear_flag(self.expand_name('{endpoint_name}.available'))
        reactive.set_flag(self.expand_name('{endpoint_name}.connected'))

    @reactive.when('endpoint.{endpoint_name}.changed')
    def changed(self):
        flags = (
            self.expand_name(
                'endpoint.{endpoint_name}.changed.database'),
            self.expand_name(
                'endpoint.{endpoint_name}.changed.username'),
            self.expand_name(
                'endpoint.{endpoint_name}.changed.hostname'),
        )
        if reactive.all_flags_set(*flags):
            for flag in flags:
                reactive.clear_flag(flag)

        if self.available():
            reactive.set_flag(self.expand_name('{endpoint_name}.available'))
        else:
            reactive.clear_flag(self.expand_name('{endpoint_name}.available'))

    @reactive.when_any('endpoint.{endpoint_name}.broken',
                       'endpoint.{endpoint_name}.departed')
    def departed(self):
        flags = (
            self.expand_name('{endpoint_name}.connected'),
            self.expand_name('{endpoint_name}.available'),
        )
        for flag in flags:
            reactive.clear_flag(flag)

    def set_db_connection_info(
            self, db_host, password, allowed_units, relation_id):
        self.relations[relation_id].to_publish['db_host'] = db_host
        self.relations[relation_id].to_publish['password'] = password
        self.relations[relation_id].to_publish['allowed_units'] = allowed_units
