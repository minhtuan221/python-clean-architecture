class TestProcessMakerService:

    def test_get_process_with_all_children(self, process_1, process_service):
        res = process_service.find_one(process_1.id)
        print(res)






