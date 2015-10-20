"""Copy transcript protein links to redis

Revision ID: 225a8b4c3902
Revises: 3492d2ee8884
Create Date: 2015-10-15 14:11:22.961417

"""

from __future__ import unicode_literals

# revision identifiers, used by Alembic.
revision = '225a8b4c3902'
down_revision = u'3492d2ee8884'

from datetime import datetime, timedelta

import redis
from alembic import op
from sqlalchemy import and_, or_, sql
import sqlalchemy as sa

from mutalyzer.config import settings


def upgrade():
    if settings.REDIS_URI is None:
        return

    connection = op.get_bind()

    redis_client = redis.StrictRedis.from_url(settings.REDIS_URI,
                                              decode_responses=True,
                                              encoding='utf-8')

    transcript_protein_links = sql.table(
        'transcript_protein_links',
        sql.column('transcript_accession', sa.String(30)),
        sql.column('protein_accession', sa.String(30)),
        sql.column('added', sa.DateTime)
    )

    negative_link_datetime = datetime.now() - \
        timedelta(seconds=settings.NEGATIVE_LINK_CACHE_EXPIRATION)

    result = connection.execute(transcript_protein_links.select().where(
        or_(and_(transcript_protein_links.c.transcript_accession.isnot(None),
                 transcript_protein_links.c.protein_accession.isnot(None)),
            transcript_protein_links.c.added >= negative_link_datetime)
    ).with_only_columns([transcript_protein_links.c.transcript_accession,
                         transcript_protein_links.c.protein_accession]))

    while True:
        chunk = result.fetchmany(1000)
        if not chunk:
            break

        pipe = redis_client.pipeline(transaction=False)

        for row in chunk:
            transcript_accession, protein_accession = row

            if transcript_accession is not None:
                key = 'ncbi:transcript-to-protein:%s' % transcript_accession
                if protein_accession is not None:
                    pipe.set(key, protein_accession)
                else:
                    pipe.setex(key, settings.NEGATIVE_LINK_CACHE_EXPIRATION,
                               '')

            if protein_accession is not None:
                key = 'ncbi:protein-to-transcript:%s' % protein_accession
                if transcript_accession is not None:
                    pipe.set(key, transcript_accession)
                else:
                    pipe.setex(key, settings.NEGATIVE_LINK_CACHE_EXPIRATION,
                               '')

        pipe.execute()


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    pass
    ### end Alembic commands ###