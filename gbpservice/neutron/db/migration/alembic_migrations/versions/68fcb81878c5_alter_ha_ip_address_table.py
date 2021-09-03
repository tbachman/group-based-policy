#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Alter HA IP address to Port ID association table to add VRF entry
Revision ID: 68fcb81878c5
Revises: f8dc1eb9deaf
Create Date: 2015-10-19 02:08:54.252877
"""

# revision identifiers, used by Alembic.
revision = '68fcb81878c5'
down_revision = 'f8dc1eb9deaf'

from alembic import op
from alembic import util
import sqlalchemy as sa
from sqlalchemy.engine import reflection


def upgrade():

    inspector = reflection.Inspector.from_engine(op.get_bind())
    pk_constraint = inspector.get_pk_constraint(
            'apic_ml2_ha_ipaddress_to_port_owner')
    op.drop_constraint(
        pk_constraint['name'],
        table_name='apic_ml2_ha_ipaddress_to_port_owner',
        type_='primary')
    op.add_column('apic_ml2_ha_ipaddress_to_port_owner',
                  sa.Column('vrf', sa.String(length=64), nullable=False))
    op.create_primary_key(
        constraint_name='apic_ml2_ha_ipaddress_to_port_owner_pk',
        table_name='apic_ml2_ha_ipaddress_to_port_owner',
        columns=['ha_ip_address', 'vrf'])

    bind = op.get_bind()
    insp = sa.engine.reflection.Inspector.from_engine(bind)
    if 'apic_ml2_ha_ipaddress_to_port_owner' in insp.get_table_names():
        try:
            from gbpservice.neutron.plugins.ml2plus.drivers.apic_aim import (
                data_migrations)

            session = sa.orm.Session(bind=bind, autocommit=True)
            data_migrations.do_ha_ip_vrf_name_insertion(session)
        except ImportError:
            util.warn("AIM schema present, but failed to import AIM libraries"
                      " - HA IP vrf name not inserted.")
        except Exception as e:
            util.warn("Caught exception inserting HA IP vrf name: %s"
                      % e)


def downgrade():
    pass
