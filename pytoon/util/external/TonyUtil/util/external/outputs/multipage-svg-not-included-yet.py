#  (C) Copyright 2012, 2013, 2018 Anthony D. Dutoi
#
#  This file is part of TonyUtil.
#
#  TonyUtil is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

def static_page(filestem,pagenumber,lastpage,page,pdf=False):
    pagination = (pagenumber,lastpage,('page-up','up-arrow'),('page-dn','dn-arrow'))
    texlabels = filestem + '/texlabels/' + str(pagenumber) + '/text*.svg'
    if pdf:  page.pdf(filestem+'/'+str(pagenumber),texlabels=texlabels)
    else:    page.svg(filestem,texlabels=texlabels,pagination=pagination)

def animated_page(filestem,pagenumber,lastpage,pagefn,count,duration,background,foreground):
    texlabels = filestem + '/texlabels/' + str(pagenumber)
    pagination = (pagenumber,lastpage,('page-up','up-arrow'),('page-dn','dn-arrow'))
    controls = (('space','B'),('R','escape','F5','P'),('left-arrow',),('right-arrow',))
    animate.svg(filestem,pagefn,count,duration,background=background,foreground=foreground,texlabels=texlabels,controls=controls,pagination=pagination)



def loop(filestem,pages,static_pdfs=False):
    if not os.path.exists(filestem):  os.makedirs(filestem)
    lastpage = False
    N = len(pages)
    m = 0
    for n,page in enumerate(pages):
        m += 1
        pagenumber = n+1
        if pagenumber==N:  lastpage = True
        pagenumber = m		# a bit hacky, m==n+1 if static_pdfs is False
        if isinstance(page,tuple):
            pagefn,count,duration,background,foreground = page
            if static_pdfs:
                A  = composite()
                if background is not None:  A += background
                A += pagefn()
                if foreground is not None:  A += foreground
                for i in range(count-2):  pagefn()
                Z  = composite()
                if background is not None:  Z += background
                Z += pagefn()
                if foreground is not None:  Z += foreground
                static_page(filestem,pagenumber  ,lastpage,A,True)
                static_page(filestem,pagenumber+1,lastpage,Z,True)
                m += 1
            else:
                animated_page(filestem,pagenumber,lastpage,pagefn,count,duration,background,foreground)
        else:
            static_page(filestem,pagenumber,lastpage,page,static_pdfs)
