# import unittest
from pytest import fixture

import cloudinary
from cloudinary import CloudinaryVideo

VIDEO_UPLOAD_PATH = "http://res.cloudinary.com/test123/video/upload/"
DEFAULT_UPLOAD_PATH = "http://res.cloudinary.com/test123/image/upload/"


@fixture
def config():
    cloudinary.config(cloud_name="test123", api_secret="1234", cname=None)
    video = CloudinaryVideo("movie")
    yield video


def test_video_thumbail(config):
    assert config.video_thumbnail() == VIDEO_UPLOAD_PATH + "movie.jpg"
    assert config.video_thumbnail(width=100) == VIDEO_UPLOAD_PATH + "w_100/movie.jpg"


def test_video_image_tag(config):
    expected_url = VIDEO_UPLOAD_PATH + "movie.jpg"
    assert config.image() == '<img src="' + expected_url + '"/>'
    expected_url = VIDEO_UPLOAD_PATH + "w_100/movie.jpg"
    assert config.image(width=100) == '<img src="' + expected_url + '" width="100"/>'


def test_video_tag(config):
    """default"""
    expected_url = VIDEO_UPLOAD_PATH + "movie"
    assert (
        config.video()
        == '<video poster="'
        + expected_url
        + '.jpg">'
        + '<source src="'
        + expected_url
        + '.webm" type="video/webm">'
        + '<source src="'
        + expected_url
        + '.mp4" type="video/mp4">'
        + '<source src="'
        + expected_url
        + '.ogv" type="video/ogg">'
        + "</video>"
    )


def test_video_tag_with_attributes(config):
    """test video attributes"""
    expected_url = VIDEO_UPLOAD_PATH + "movie"
    assert config.video(
        autoplay=1,
        controls=True,
        loop=True,
        muted="true",
        preload=True,
        style="border: 1px",
    ) == (
        (
            '<video autoplay="1" controls loop muted="true" poster="{expected_url}.jpg"'
            + ' preload style="border: 1px">'
            + '<source src="{expected_url}.webm" type="video/webm">'
            + '<source src="{expected_url}.mp4" type="video/mp4">'
            + '<source src="{expected_url}.ogv" type="video/ogg">'
            "</video>"
        ).format(expected_url=expected_url)
    )


def test_video_tag_with_transformation(config):
    """test video attributes"""
    options = {
        "source_types": "mp4",
        "html_height": "100",
        "html_width": "200",
        "video_codec": {"codec": "h264"},
        "audio_codec": "acc",
        "start_offset": 3,
    }

    expected_url = VIDEO_UPLOAD_PATH + "ac_acc,so_3,vc_h264/movie"
    assert (
        config.video(**options)
        == '<video height="100" poster="'
        + expected_url
        + '.jpg" '
        + 'src="'
        + expected_url
        + '.mp4" width="200">'
        + "</video>"
    )

    del options["source_types"]
    assert (
        config.video(**options)
        == '<video height="100" poster="'
        + expected_url
        + '.jpg" width="200">'
        + '<source src="'
        + expected_url
        + '.webm" type="video/webm">'
        + '<source src="'
        + expected_url
        + '.mp4" type="video/mp4">'
        + '<source src="'
        + expected_url
        + '.ogv" type="video/ogg">'
        + "</video>"
    )

    del options["html_height"]
    del options["html_width"]
    options["width"] = 250
    expected_url = VIDEO_UPLOAD_PATH + "ac_acc,so_3,vc_h264,w_250/movie"
    assert (
        config.video(**options)
        == '<video poster="'
        + expected_url
        + '.jpg" width="250">'
        + '<source src="'
        + expected_url
        + '.webm" type="video/webm">'
        + '<source src="'
        + expected_url
        + '.mp4" type="video/mp4">'
        + '<source src="'
        + expected_url
        + '.ogv" type="video/ogg">'
        + "</video>"
    )

    expected_url = VIDEO_UPLOAD_PATH + "ac_acc,c_fit,so_3,vc_h264,w_250/movie"
    options["crop"] = "fit"
    assert (
        config.video(**options)
        == '<video poster="'
        + expected_url
        + '.jpg">'
        + '<source src="'
        + expected_url
        + '.webm" type="video/webm">'
        + '<source src="'
        + expected_url
        + '.mp4" type="video/mp4">'
        + '<source src="'
        + expected_url
        + '.ogv" type="video/ogg">'
        + "</video>"
    )


def test_video_tag_with_fallback(config):
    expected_url = VIDEO_UPLOAD_PATH + "movie"
    fallback = '<span id="spanid">Cannot display video</span>'
    assert (
        config.video(fallback_content=fallback)
        == '<video poster="'
        + expected_url
        + '.jpg">'
        + '<source src="'
        + expected_url
        + '.webm" type="video/webm">'
        + '<source src="'
        + expected_url
        + '.mp4" type="video/mp4">'
        + '<source src="'
        + expected_url
        + '.ogv" type="video/ogg">'
        + fallback
        + "</video>"
    )
    assert (
        config.video(fallback_content=fallback, source_types="mp4")
        == '<video poster="'
        + expected_url
        + '.jpg" src="'
        + expected_url
        + '.mp4">'
        + fallback
        + "</video>"
    )


def test_video_tag_with_source_types(config):
    expected_url = VIDEO_UPLOAD_PATH + "movie"
    assert (
        config.video(source_types=["ogv", "mp4"])
        == '<video poster="'
        + expected_url
        + '.jpg">'
        + '<source src="'
        + expected_url
        + '.ogv" type="video/ogg">'
        + '<source src="'
        + expected_url
        + '.mp4" type="video/mp4">'
        + "</video>"
    )


def test_video_tag_with_source_transformation(config):
    expected_url = VIDEO_UPLOAD_PATH + "q_50/w_100/movie"
    expected_ogv_url = VIDEO_UPLOAD_PATH + "q_50/q_70,w_100/movie"
    expected_mp4_url = VIDEO_UPLOAD_PATH + "q_50/q_30,w_100/movie"

    assert (
        config.video(
            width=100,
            transformation={"quality": 50},
            source_transformation={"ogv": {"quality": 70}, "mp4": {"quality": 30}},
        )
        == '<video poster="'
        + expected_url
        + '.jpg" width="100">'
        + '<source src="'
        + expected_url
        + '.webm" type="video/webm">'
        + '<source src="'
        + expected_mp4_url
        + '.mp4" type="video/mp4">'
        + '<source src="'
        + expected_ogv_url
        + '.ogv" type="video/ogg">'
        + "</video>"
    )

    assert (
        config.video(
            width=100,
            transformation={"quality": 50},
            source_transformation={"ogv": {"quality": 70}, "mp4": {"quality": 30}},
            source_types=["webm", "mp4"],
        )
        == '<video poster="'
        + expected_url
        + '.jpg" width="100">'
        + '<source src="'
        + expected_url
        + '.webm" type="video/webm">'
        + '<source src="'
        + expected_mp4_url
        + '.mp4" type="video/mp4">'
        + "</video>"
    )


def test_video_tag_with_poster(config):
    expected_url = VIDEO_UPLOAD_PATH + "movie"

    expected_poster_url = "http://image/somewhere.jpg"
    assert (
        config.video(poster=expected_poster_url, source_types="mp4")
        == '<video poster="'
        + expected_poster_url
        + '" src="'
        + expected_url
        + '.mp4"></video>'
    )

    expected_poster_url = VIDEO_UPLOAD_PATH + "g_north/movie.jpg"
    assert (
        config.video(poster={"gravity": "north"}, source_types="mp4")
        == '<video poster="'
        + expected_poster_url
        + '" src="'
        + expected_url
        + '.mp4"></video>'
    )

    expected_poster_url = DEFAULT_UPLOAD_PATH + "g_north/my_poster.jpg"
    assert (
        config.video(
            poster={"gravity": "north", "public_id": "my_poster", "format": "jpg"},
            source_types="mp4",
        )
        == '<video poster="'
        + expected_poster_url
        + '" src="'
        + expected_url
        + '.mp4"></video>'
    )

    assert (
        config.video(poster=None, source_types="mp4")
        == '<video src="' + expected_url + '.mp4"></video>'
    )

    assert (
        config.video(poster=False, source_types="mp4")
        == '<video src="' + expected_url + '.mp4"></video>'
    )


def test_video_tag_default_sources(config):
    expected_url = VIDEO_UPLOAD_PATH + "{}movie.{}"

    assert '<video poster="' + expected_url.format(
        "", "jpg"
    ) + '">' + '<source src="' + expected_url.format(
        "vc_h265/", "mp4"
    ) + '" type="video/mp4; codecs=hev1">' + '<source src="' + expected_url.format(
        "vc_vp9/", "webm"
    ) + '" type="video/webm; codecs=vp9">' + '<source src="' + expected_url.format(
        "vc_auto/", "mp4"
    ) + '" type="video/mp4">' + '<source src="' + expected_url.format(
        "vc_auto/", "webm"
    ) + '" type="video/webm">' + "</video>" == config.video(
        poster=expected_url.format("", "jpg"),
        sources=config.default_video_sources,
    )


def test_video_tag_custom_sources(config):
    custom_sources = [
        {
            "type": "mp4",
            "codecs": "vp8, vorbis",
            "transformations": {"video_codec": "auto"},
        },
        {
            "type": "webm",
            "codecs": "avc1.4D401E, mp4a.40.2",
            "transformations": {"video_codec": "auto"},
        },
    ]
    expected_url = VIDEO_UPLOAD_PATH + "{}movie.{}"

    assert '<video poster="' + expected_url.format(
        "", "jpg"
    ) + '">' + '<source src="' + expected_url.format(
        "vc_auto/", "mp4"
    ) + '" type="video/mp4; codecs=vp8, vorbis">' + '<source src="' + expected_url.format(
        "vc_auto/", "webm"
    ) + '" type="video/webm; codecs=avc1.4D401E, mp4a.40.2">' + "</video>" == config.video(
        poster=expected_url.format("", "jpg"), sources=custom_sources
    )


def test_video_tag_sources_codecs_array(config):
    custom_sources = [
        {
            "type": "mp4",
            "codecs": ["vp8", "vorbis"],
            "transformations": {"video_codec": "auto"},
        },
        {
            "type": "webm",
            "codecs": ["avc1.4D401E", "mp4a.40.2"],
            "transformations": {"video_codec": "auto"},
        },
    ]
    expected_url = VIDEO_UPLOAD_PATH + "{}movie.{}"

    assert '<video poster="' + expected_url.format(
        "", "jpg"
    ) + '">' + '<source src="' + expected_url.format(
        "vc_auto/", "mp4"
    ) + '" type="video/mp4; codecs=vp8, vorbis">' + '<source src="' + expected_url.format(
        "vc_auto/", "webm"
    ) + '" type="video/webm; codecs=avc1.4D401E, mp4a.40.2">' + "</video>" == config.video(
        poster=expected_url.format("", "jpg"), sources=custom_sources
    )


def test_video_tag_sources_with_transformation(config):
    """test video tag with (sources) attribute. It replaces source_types to work with codecs list"""
    options = {
        "source_types": "mp4",
        "html_height": "100",
        "html_width": "200",
        "video_codec": {"codec": "h264"},
        "audio_codec": "acc",
        "start_offset": 3,
        "sources": config.default_video_sources,
    }
    expected_url = VIDEO_UPLOAD_PATH + "ac_acc,so_3,{}movie.{}"

    assert '<video height="100" poster="' + expected_url.format(
        "vc_h264/", "jpg"
    ) + '" width="200">' + '<source src="' + expected_url.format(
        "vc_h265/", "mp4"
    ) + '" type="video/mp4; codecs=hev1">' + '<source src="' + expected_url.format(
        "vc_vp9/", "webm"
    ) + '" type="video/webm; codecs=vp9">' + '<source src="' + expected_url.format(
        "vc_auto/", "mp4"
    ) + '" type="video/mp4">' + '<source src="' + expected_url.format(
        "vc_auto/", "webm"
    ) + '" type="video/webm">' + "</video>" == config.video(
        poster=expected_url.format("vc_h264/", "jpg"), **options
    )
