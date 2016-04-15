

class myTreeView(QTreeView):

    def __init__(self, parent=None):
        super(myTreeView, self).__init__(parent)

        self.myModel = myModel()
        self.setModel(self.myModel)

        self.dragEnabled()
        self.acceptDrops()
        self.showDropIndicator()
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.connect(self.model(),
SIGNAL("dataChanged(QModelIndex,QModelIndex)"), self.change)
        self.expandAll()

    def change(self, topLeftIndex, bottomRightIndex):
        self.update(topLeftIndex)
        self.expandAll()
        self.expanded()

    def expanded(self):
        for column in range(self.model().columnCount(QModelIndex())):
            self.resizeColumnToContents(column)