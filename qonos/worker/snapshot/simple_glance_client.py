#    Copyright 2014 Rackspace
#
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
import glanceclient.client as client
import qonos.openstack.common.log as logging

LOG = logging.getLogger(__name__)


class GlanceClient(object):

    def __init__(self, endpoint, token, version=1):
        self.endpoint = endpoint
        self.version = version
        self.token = token
        self.client = None

    # Seam for testing
    def _create_client(self, version, endpoint, token):
        return client.Client(version=version, endpoint=endpoint, token=token)

    def _get_client(self):
        return self._create_client(self.version, self.endpoint, self.token)

    def get_image(self, image_id):
        return self._get_client().images.get(image_id)

    def _get_si_filter(self, instance_id):
        return {
            "org.openstack__1__created_by": "scheduled_images_service",
            "instance_uuid": instance_id
        }

    def _get_v1_images(self, instance_id, filters):
        v1_filters = {
            "status": "ACTIVE",
            "properties": self._get_si_filter(instance_id)
        }
        return self._get_client().images.list(filters=v1_filters)

    def _get_v2_images(self, instance_id, filters):
        v2_filters = self._get_si_filter(instance_id)
        v2_filters['status'] = "ACTIVE"
        return self._get_client().images.list(filters=v2_filters)

    def get_scheduled_images_by_instance(self, instance_id, filters=None):
        if filters is None:
            filters = self._get_si_filter(instance_id)

        if self.version == 1:
            return self._get_v1_images(instance_id, filters)
        else:
            return self._get_v2_images(instance_id, filters)

    def delete_image(self, image_id):
        self._get_client().images.delete(image_id)