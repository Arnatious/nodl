from pathlib import Path
import lxml.etree as etree

import pytest

import nodl.nodl_parse as nodl_parse
import nodl.nodl_types as nodl_types


@pytest.fixture()
def valid_nodl() -> etree._ElementTree:
    return etree.parse(str(Path("test") / "nodl.xml"))


def test_parse_element_tree(mocker):
    not_interface: etree._Element = etree.Element("notinterface")
    not_interface.append(etree.Element('stillnotelement'))
    mock_et = mocker.patch(
        "nodl.nodl_parse.etree._ElementTree", **{"getroot.return_value": not_interface}
    )
    with pytest.raises(nodl_parse.InvalidNoDLException) as excinfo:
        nodl_parse.parse_element_tree(mock_et)
    assert "No interface tag in" in str(excinfo.value)


def test_parse_nodl_file_valid(mocker):
    mocker.patch("nodl.nodl_parse.Interface_v1")

    # Test if accepts a valid xml file
    nodl_parse.parse_nodl_file(Path("test/nodl.xml"))


def test_parse_nodl_file_invalid(mocker):
    mocker.patch("nodl.nodl_parse.etree.parse")

    interface_no_version = etree.Element("interface")
    mocker.patch("nodl.nodl_parse.parse_element_tree", return_value=interface_no_version)
    with pytest.raises(nodl_parse.InvalidNoDLException) as excinfo:
        nodl_parse.parse_nodl_file(Path())
    assert "Missing version attribute in 'interface'" in str(excinfo.value)

    interface_future_version = etree.Element(
        "interface", {"version": str(nodl_parse.NODL_MAX_SUPPORTED_VERSION + 1)}
    )
    mocker.patch("nodl.nodl_parse.parse_element_tree", return_value=interface_future_version)
    with pytest.raises(nodl_parse.UnsupportedInterfaceException) as excinfo:
        nodl_parse.parse_nodl_file(Path())
    assert "Unsupported interface version" in str(excinfo)


class TestInterface_v1:

    def test___init___(self, valid_nodl):
        assert nodl_parse.Interface_v1(valid_nodl)

    def test_parse_action(self):
        element: etree._Element = etree.Element("action", {
            "name": "foo",
            "type": "bar",
            "server": "True",
            "client": "False"
        })

        assert type(nodl_parse.Interface_v1.parse_action(element)) is nodl_types.Action

        element.attrib['server'] = "False"
        with pytest.warns(nodl_parse.NoNodeInterfaceWarning):
            assert type(nodl_parse.Interface_v1.parse_action(element)) is nodl_types.Action
