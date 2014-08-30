# pylint: disable-msg=E1101,W0613,W0603

from __future__ import unicode_literals

import pandas

from pyopendata.base import RDFStore, DataSource

class CKANStore(RDFStore):
    """
    Storage class to read data via CKAN API

    Parameters
    ----------
    url : string
        URL for CKAN API

    """
    def __init__(self, url, **kwargs):
        RDFStore.__init__(self, url=url, **kwargs)

        if self.url.endswith('api'):
            # remove '/api'
            self.url = self.url[:-4]

        # cache
        self._packages = None
        self._groups = None
        self._tags = None

    def is_valid(self):
        """
        Check whether the site has valid API.

        Returns
        -------
        is_valid : bool
        """
        try:
            response = self._requests_get('/api/action/site_read')
            results = self._validate_response(response)
            return True
        except self._connection_errors:
            return False

    def get(self, object_id):
        """
        Get instance related to object_id. First try to get_resource, then get_package.

        Parameters
        ----------
        object_id : str
            id to specify resource or package

        Returns
        -------
        result : CKANResouce or CKANPackage
        """
        try:
            return self.get_resource(object_id)
        except self._connection_errors:
            pass
        try:
            return self.get_package(object_id)
        except self._connection_errors:
            raise

    def get_package(self, package_id):
        """
        Get package related to package_id.

        Parameters
        ----------
        package_id : str
            id to specify package

        Returns
        -------
        result : CKANPackage
        """
        params = dict(id=package_id)
        response = self._requests_get('/api/action/package_show', params=params)
        results = self._validate_response(response)
        return CKANPackage(_store=self, **results)

    def get_resource(self, resource_id):
        """
        Get package related to resource_id.

        Parameters
        ----------
        resource_id : str
            id to specify resource

        Returns
        -------
        result : CKANResource
        """
        params = dict(id=resource_id)
        response = self._requests_get('/api/action/resource_show', params=params)
        results = self._validate_response(response)
        return CKANResource(_store=self, **results)

    def get_resources_from_tag(self, tag):
        params = dict(id=tag)
        response = self._requests_get('/api/action/tag_show', params=params)
        results = self._validate_response(response)
        results = results['packages']
        return [CKANResource(_store=self, **r) for r in results]

    def get_packages_from_group(self, group_id):
        params = dict(id=group_id)
        response = self._requests_get('/api/action/group_show', params=params)
        results = self._validate_response(response)
        results = results['packages']
        return [CKANPackage(_store=self, **r) for r in results]

    def search(self, search_string):
        # get smaller object to larger object (resource -> package)
        try:
            return self.search_resource(search_string)
        except self._connection_errors:
            pass
        try:
            return self.search_package(search_string)
        except self._connection_errors:
            raise

    def search_package(self, search_string):
        params = dict(q=search_string)
        response = self._requests_get('/api/action/package_search', params=params)
        results = self._validate_response(response)
        results = results['results']
        return [CKANPackage(_store=self, **r) for r in results]

    def search_resource(self, search_string):
        # different params from search_packages
        # params = dict(query=search_string)
        # response = requests.get('{0}/api/action/resource_search'.format(self.url), params=params)

        # avoid escape search string (:)

        request_url = '/api/action/resource_search?query={0}'.format(search_string)
        response = self._requests_get(request_url)
        results = self._validate_response(response)
        results = results['results']
        return [CKANResource(_store=self, **r) for r in results]

    @property
    def datasets(self):
        return self.packages

    @property
    def packages(self):
        if self._packages is None:
            response = self._requests_get('/api/action/package_list')
            results = self._validate_response(response)
            if isinstance(results, list):
                self._packages = [CKANPackage(_store=self, name=r) for r in results]
                # self._packages = results
            elif isinstance(results, dict):
                # internally calls ``current_package_list_with_resources``?
                results = results['results']
                self._packages = [CKANPackage(_store=self, **r) for r in results]
            else:
                raise ValueError(type(results), results)
        return self._packages

    @property
    def groups(self):
        if self._groups is None:
            response = self._requests_get('/api/action/group_list')
            self._groups = self._validate_response(response)
        return self._groups

    @property
    def tags(self):
        if self._tags is None:
            response = self._requests_get('/api/action/tag_list')
            self._tags= self._validate_response(response)
        return self._tags

    def _validate_response(self, response):
        if response.status_code != 200:
            raise ValueError(response.status_code)

        response_dict = response.json()
        if response_dict['success'] is not True:
            raise valueError(responce_dict['message'])
        return response_dict['result']


class CKANPackage(RDFStore):

    def __init__(self, _store=None, resources=None, name=None, **kwargs):
        RDFStore.__init__(self, **kwargs)

        if _store is None:
            raise ValueError('_store must be passed')
        else:
            self.store = _store
        if name is None:
            raise ValueError("Package doesn't have 'name' attribute")
        else:
            self.name = name

        if isinstance(resources, list):
            self._resources = [CKANResource(_store=self.store, **r) for r in resources]
        else:
            self._resources = None

    def __unicode__(self):
        source_len = len(self.resources)
        if source_len == 0:
            return '{0} (Empty)'.format(self.name)
        elif source_len == 1:
            return '{0} (1 resource)'.format(self.name)
        else:
            return '{0} ({1} resources)'.format(self.name, source_len)

    @property
    def resources(self):
        # if resources is blank, retrieve from the store
        if self._resources is None:
            self._resources = self.store.get_package(self.name).resources
        return self._resources

    def read(self, raw=False, **kwargs):
        """
        Read data from its resource if the number of resource is 1.
        Otherwise, raise ValueError.

        Parameters
        ----------
        raw : bool, default False
            If False, return pandas.DataFrame. If True, return raw data
        kwargs:
            Keywords passed to pandas.read_xxx function

        Returns
        -------
        data : pandas.DataFrame or requests.raw.data
        """
        source_len = len(self.resources)
        if source_len == 0:
            if raw:
                return None
            else:
                return pandas.DataFrame()
        elif source_len == 1:
            return self.resources[0].read(raw=raw, **kwargs)
        else:
            raise ValueError('Package has {0} resources. Specify target CKANResource to read'.format(source_len))


class CKANResource(RDFStore):
    _attrs = ['size_text']
    _supported_formats = ('CSV', 'JSON', 'XLS')

    def __init__(self, _store=None, resources=None, **kwargs):
        RDFStore.__init__(self, **kwargs)

        if _store is None:
            raise ValueError('_store must be passed')
        else:
            self.store = _store

        if resources is None:
            self.resources = None
        elif isinstance(resources, list):
            self.resources = [CKANResource(_store=self.store, **r) for r in resources]
        else:
            raise ValueError(type(resources), resources)

    def __unicode__(self):
        rep_str = """Resource ID: {id}
Resource Name: {name}
Resource URL: {url}
Format: {format}, Size: {size}""".format(id=self.id, name=self.name,
                                         url=self.url,
                                         format=self.format,
                                         size=self.size_text)
        return rep_str

    def read(self, raw=False, **kwargs):
        """
        Read data from resource

        Parameters
        ----------
        raw : bool, default False
            If False, return pandas.DataFrame. If True, return raw data
        kwargs:
            Keywords passed to pandas.read_xxx function

        Returns
        -------
        data : pandas.DataFrame or requests.raw.data

        Notes
        -----
        - When the resource format is other than CSV, parsing pandas.DataFrame may fail.
          Use ``raw=True`` to get raw data in such cases.
        """
        if self.resources is None:
            return DataSource.read(self, raw=raw, **kwargs)
        else:
            source_len = len(self.resources)
            if source_len == 0:
                return pandas.DataFrame()
            elif source_len == 1:
                return self.resources[0].read(raw=raw, **kwargs)
            else:
                raise ValueError('Package has {0} resources. Use CKANResource.read()'.format(source_len))

    def _read(self, **kwargs):
        if self.url is None:
            raise ValueError('Unable to read data because url is None')
        if self.format in ('CSV', 'CSV/TXT'):
            return pandas.read_csv(self.url, **kwargs)
        elif self.format == 'XLS':
            return pandas.read_excel(self.url, **kwargs)
        elif self.format == 'JSON':
            return pandas.read_json(self.url, **kwargs)
        elif self.format == 'N/A':
            raise ValueError('{0} is not available on the store'.format(self.name))
        else:
            raise ValueError('Unsupported read format: {0}'.format(self.format))
