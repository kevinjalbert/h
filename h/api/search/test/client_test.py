# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import mock
import pytest

from h.api.search import client


@pytest.mark.usefixtures('elasticsearch', 'presenters')
class TestIndexAnnotation:

    def test_it_presents_the_annotation(self):
        request = mock.Mock()
        annotation = mock.Mock()

        self.client().index_annotation(request, annotation)

        client.presenters.AnnotationJSONPresenter.assert_called_once_with(
            request, annotation)

    def test_it_indexes_the_annotation(self):
        client_ = self.client()

        client_.index_annotation(mock.Mock(), mock.Mock())

        client_.conn.index.assert_called_once_with(
            index='hypothesis',
            doc_type='annotation',
            body=client.presenters.AnnotationJSONPresenter.return_value.asdict.return_value,
            id='test_annotation_id',
        )

    def test_it_inserts_the_source_field(self):
        client_ = self.client()
        annotation = mock.Mock()

        client_.index_annotation(mock.Mock(), annotation)

        assert client_.conn.index.call_args[1]['body']['target'][0]['scope'] == [
            annotation.target_uri_normalized]

    def client(self):
        return client.Client(
            host='localhost',
            index='hypothesis',
        )

    @pytest.fixture
    def elasticsearch(self, monkeypatch):
        monkeypatch.setattr(
            'h.api.search.client.elasticsearch',
            mock.Mock(spec=client.elasticsearch),
        )

    @pytest.fixture
    def presenters(self, monkeypatch):
        monkeypatch.setattr(
            'h.api.search.client.presenters',
            mock.Mock(spec=client.presenters),
        )
        client.presenters.AnnotationJSONPresenter.return_value = mock.Mock(
            asdict=mock.Mock(
                return_value={
                    'id': 'test_annotation_id',
                    'target': [
                        {
                            'source': 'http://example.com/example',
                        },
                    ],
                }
            )
        )