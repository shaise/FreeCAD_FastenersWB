from pytest import fixture
from utils import csv2dict

TEST_DATA = '''"Dia","P","b","dk_theo","dk_mean","k","r","s","t"
    "#0",0.3175,6.096,3.5052,3.2385,1.1176,0.0762,0.889,0.635
    "#1",0.396875,7.4168,4.2672,3.9497,1.3716,0.09271,1.27,0.7874'''


@fixture
def create_fs_csv(tmp_path):
    fs_data = tmp_path / 'csv_test'
    fs_data.mkdir()
    fs_csv = fs_data / '1.csv'
    fs_csv.write_text(TEST_DATA)
    return str(fs_csv)


def test_csv2dict(create_fs_csv):
    expected = {
        '#0': (0.3175, 6.096, 3.5052, 3.2385, 1.1176, 0.0762, 0.889, 0.635),
        '#1': (0.396875, 7.4168, 4.2672, 3.9497, 1.3716, 0.09271, 1.27, 0.7874),
    }
    result = csv2dict(create_fs_csv, "test")
    assert result["test"] == expected
